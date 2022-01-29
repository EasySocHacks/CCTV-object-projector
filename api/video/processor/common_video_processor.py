from abc import ABC, abstractmethod
from queue import Queue, Empty
from threading import Thread

import cv2
import dlib as dlib
from PIL import Image

from bbox_expander.bbox_expander import BboxExpander
from detector.pool import DetectorPool


class CommonVideoProcessor(ABC):
    def __init__(self, skip_frame_count, frame_processor_count, detector_pool: DetectorPool, bbox_expander: BboxExpander):
        self.skip_frame_count = skip_frame_count
        self.frame_processor_count = frame_processor_count
        self.detector_pool = detector_pool
        self.bbox_expander = bbox_expander

        self.__trackers = []

        self.last_delete_frame = 0
        self.current_output_frame = 0
        self.max_frame_count = float('inf')
        self.done_processing = False

        self.__frame_processors = []
        for i in range(frame_processor_count):
            thread = Thread(target=self.__process_frame, args=(i,))
            self.__frame_processors.append(thread)

        self.__outputs = {}

        self.__thread_suggestions = [Queue()] * (len(self.__frame_processors) + 1)
        self.__suggestion_collector_thread = Thread(target=self.__collect_suggests)

        self.__frame_processor_tasks = [Queue()] * len(self.__frame_processors)
        self.__main_processor_thread = Thread(target=self.__process_video)

    def process(self):
        self._abs__process()

        self.__suggestion_collector_thread.start()
        self.__main_processor_thread.start()

        for thread in self.__frame_processors:
            thread.start()

    def __process_frame(self, thread_id):
        while self.__frame_processor_tasks[thread_id].qsize() > 0 or self._abs__has_next_frame():
            try:
                frame_id, frame = self.__frame_processor_tasks[thread_id].get_nowait()
                data = []

                bboxes, classes, scores = self.detector_pool.detect(frame, thread_id)

                for obj_bbox, obj_class, obj_score in zip(bboxes, classes, scores):
                    if obj_class != 0:
                        continue

                    if obj_score < 0.75:
                        continue

                    data.append(('person', obj_bbox))

                    croped_frame = frame[int(obj_bbox[1]):int(obj_bbox[3]), int(obj_bbox[0]):int(obj_bbox[2])]

                    expand_bbox = self.bbox_expander.expand(
                        Image.fromarray(cv2.cvtColor(croped_frame, cv2.COLOR_BGR2RGB)),
                        obj_bbox
                    )

                    cv2.rectangle(
                        frame,
                        (int(expand_bbox[0]), int(expand_bbox[1])),
                        (int(expand_bbox[2]), int(expand_bbox[3])),
                        (0, 0, 255)
                    )

                self.__thread_suggestions[thread_id].put((frame_id, frame, data))

                self.__frame_processor_tasks[thread_id].task_done()
            except Exception as e:
                print(e)
                continue

    @abstractmethod
    def _abs__process(self):
        pass

    @abstractmethod
    def _abs__has_next_frame(self):
        pass

    @abstractmethod
    def _abs__next_frame(self):
        pass

    def __process_video(self):
        frame_id = 0
        while self._abs__has_next_frame():
            try:
                frame = self._abs__next_frame()
                if frame_id % self.skip_frame_count == 0:
                    self.__frame_processor_tasks[
                        (frame_id // self.skip_frame_count) % self.frame_processor_count].put((frame_id, frame))
                else:
                    self.__thread_suggestions[-1].put((frame_id, frame, None))
                frame_id += 1
            except Empty:
                continue

        self.max_frame_count = frame_id - 1
        self.done_processing = True

    def __collect_suggests(self):
        collect = True
        while collect or self.has_next_frame():
            collect = False

            if self.current_output_frame - self.last_delete_frame > 3 * self.skip_frame_count:
                for i in range(3 * self.skip_frame_count):
                    del self.__outputs[self.last_delete_frame]
                    self.last_delete_frame += 1

            cnt = 0
            for suggestion in self.__thread_suggestions:
                cnt += 1
                try:
                    frame_id, frame, data = suggestion.get_nowait()
                    collect = True

                    self.__outputs[frame_id] = (frame, data)

                    suggestion.task_done()
                except Empty:
                    continue

    def has_next_frame(self):
        return self._abs__has_next_frame() or self.max_frame_count > self.current_output_frame

    def next_frame(self):
        if self.current_output_frame not in self.__outputs:
            raise Exception

        frame, data = self.__outputs[self.current_output_frame]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if self.current_output_frame % self.skip_frame_count == 0:
            self.__trackers = []

            for obj_class, obj_bbox in data:
                self.__trackers.append(dlib.correlation_tracker())
                self.__trackers[-1].start_track(
                    rgb_frame,
                    dlib.rectangle(
                        int(obj_bbox[0]),
                        int(obj_bbox[1]),
                        int(obj_bbox[2]),
                        int(obj_bbox[3])
                    )
                )
        else:
            for tracker in self.__trackers:
                tracker.update(rgb_frame)
                tracker_position = tracker.get_position()

                cv2.rectangle(
                    frame,
                    (int(tracker_position.left()), int(tracker_position.top())),
                    (int(tracker_position.right()), int(tracker_position.bottom())),
                    (255, 0, 0)
                )

        self.current_output_frame += 1

        return frame

    @abstractmethod
    def _abs__join(self):
        pass

    def join(self):
        self._abs__join()

        for thread in self.__frame_processors:
            thread.join()

        self.__main_processor_thread.join()
        self.__suggestion_collector_thread.join()

        for suggestion in self.__thread_suggestions:
            suggestion.join()

        for task in self.__frame_processor_tasks:
            task.join()
