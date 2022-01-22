from abc import ABC, abstractmethod
from queue import Queue, Empty
from threading import Thread

import cv2

from detector.pool import DetectorPool


class CommonVideoProcessor(ABC):
    def __init__(self, skip_frame_count, frame_processor_count, detector_pool: DetectorPool):
        self.skip_frame_count = skip_frame_count
        self.frame_processor_count = frame_processor_count
        self.detector_pool = detector_pool

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
        self.__suggestion_collector_thread.start()

        self.__frame_processor_tasks = [Queue()] * len(self.__frame_processors)
        self.__main_processor_thread = Thread(target=self.__process_video)
        self.__main_processor_thread.start()

        for thread in self.__frame_processors:
            thread.start()

    def __process_frame(self, thread_id):
        while True:
            frame_id, frame = self.__frame_processor_tasks[thread_id].get()

            bboxes, classes, scores = self.detector_pool.detect(frame, thread_id)
            for obj_bbox, obj_class, obj_score in zip(bboxes, classes, scores):
                if obj_class != 0:
                    continue

                if obj_score < 0.75:
                    continue

                cv2.rectangle(frame, (obj_bbox[0], obj_bbox[1]), (obj_bbox[2], obj_bbox[3]), (0, 0, 255))

            self.__thread_suggestions[thread_id].put((frame_id, frame))

    @abstractmethod
    def _abs__has_next_frame(self):
        pass

    @abstractmethod
    def _abs__next_frame(self):
        pass

    def __process_video(self):
        frame_id = 0
        while self._abs__has_next_frame():
            frame = self._abs__next_frame()
            if frame_id % self.skip_frame_count == 0:
                self.__frame_processor_tasks[
                    (frame_id // self.skip_frame_count) % self.frame_processor_count].put((frame_id, frame))
            else:
                self.__thread_suggestions[-1].put((frame_id, frame))
            frame_id += 1

        self.max_frame_count = frame_id
        self.done_processing = True

        for suggestion_queue in self.__thread_suggestions:
            suggestion_queue.join()

        for thread in self.__frame_processors:
            thread.join()

    def __collect_suggests(self):
        while True:
            if self.current_output_frame - self.last_delete_frame >= 3 * self.skip_frame_count:
                for i in range(3 * self.skip_frame_count):
                    del self.__outputs[self.last_delete_frame]
                    self.last_delete_frame += 1

            for suggestion in self.__thread_suggestions:
                try:
                    frame_id, frame = suggestion.get_nowait()

                    self.__outputs[frame_id] = frame

                    suggestion.task_done()
                except Empty as e:
                    continue

    def has_next_frame(self):
        return self.max_frame_count > self.current_output_frame

    def next_frame(self):
        while self.current_output_frame not in self.__outputs:
            pass

        frame = self.__outputs[self.current_output_frame]
        self.current_output_frame += 1

        return frame

    def close(self):
        self.__suggestion_collector_thread.join()
        self.__main_processor_thread.join()
