import copy
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger
from queue import Empty
from threading import Thread

import cv2
import dlib as dlib
from PIL import Image

from bbox_expander.bbox_expander import BboxExpander
from bbox_expander.pool.bbox_expander_pool import BboxExpanderPool
from detector.pool import DetectorPool


class CommonVideoProcessor(ABC):
    def __init__(self,
                 batch_frame_size,
                 max_future_frame_count,
                 detector_pool: DetectorPool,
                 bbox_expander_pool: BboxExpanderPool):
        if batch_frame_size > max_future_frame_count:
            raise Exception

        self.batch_frame_size = batch_frame_size
        self.max_future_frame_count = max_future_frame_count
        self.detector_pool = detector_pool
        self.bbox_expander_pool = bbox_expander_pool

        self.thread_pool = ThreadPoolExecutor(max_workers=int(max_future_frame_count / batch_frame_size))

        self.future_frames = [-1] * self.max_future_frame_count
        for index, _ in enumerate(self.future_frames):
            self.future_frames[index] = index

        self.done_processing = False

        self.current_output_frame = 0
        self.max_frame_count = float('inf')

        self.__main_processor_thread = Thread(target=self.__process_video)

        self.logger = getLogger()

    def process(self):
        self._abs__process()

        self.__main_processor_thread.start()

    def __process_frame_batch(self, batch):
        self.logger.info("Start process frame batch [{}-{}]"
                         .format(batch[0][0], batch[0][0] + self.batch_frame_size - 1))

        trackers = []
        expands = []

        for index, (frame_id, frame) in enumerate(batch):
            self.logger.info("Start process frame {}".format(frame_id))

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if index == 0:
                bboxes, classes, scores = self.detector_pool.detect(frame)

                for obj_bbox, obj_class, obj_score in zip(bboxes, classes, scores):
                    if obj_class != 0:
                        continue

                    if obj_score < 0.6:
                        continue

                    trackers.append(dlib.correlation_tracker())
                    trackers[-1].start_track(
                        rgb_frame,
                        dlib.rectangle(
                            int(obj_bbox[0]),
                            int(obj_bbox[1]),
                            int(obj_bbox[2]),
                            int(obj_bbox[3])
                        )
                    )

                    cv2.rectangle(
                        frame,
                        (int(obj_bbox[0]), int(obj_bbox[1])),
                        (int(obj_bbox[2]), int(obj_bbox[3])),
                        (0, 0, 255)
                    )

                    croped_image = rgb_frame[
                                   int(obj_bbox[1]):int(obj_bbox[3]),
                                   int(obj_bbox[0]):int(obj_bbox[2])
                                   ]

                    expand = self.bbox_expander_pool.expand(Image.fromarray(croped_image))
                    expand_bbox = BboxExpander.apply_expand(obj_bbox, expand)

                    cv2.rectangle(
                        frame,
                        (int(expand_bbox[0]), int(expand_bbox[1])),
                        (int(expand_bbox[2]), int(expand_bbox[3])),
                        (255, 0, 0)
                    )

                    expands.append(expand)

            else:
                for tracker, expand in zip(trackers, expands):
                    tracker.update(rgb_frame)
                    tracker_position = tracker.get_position()

                    bbox = [
                        tracker_position.left(),
                        tracker_position.top(),
                        tracker_position.right(),
                        tracker_position.bottom()
                    ]

                    expand_bbox = BboxExpander.apply_expand(bbox, expand)

                    cv2.rectangle(
                        frame,
                        (int(expand_bbox[0]), int(expand_bbox[1])),
                        (int(expand_bbox[2]), int(expand_bbox[3])),
                        (255, 0, 0)
                    )

        self.logger.info("End process frame batch [{}-{}]".format(batch[0][0], batch[0][0] + self.batch_frame_size - 1))

        for frame_id, frame in batch:
            while self.future_frames[frame_id % self.max_future_frame_count] != frame_id:
                continue

            self.logger.info("Push frame {} onto {} with value {}".format(
                frame_id,
                frame_id % self.max_future_frame_count,
                self.future_frames[frame_id % self.max_future_frame_count]
            ))

            self.future_frames[frame_id % self.max_future_frame_count] = frame

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
        self.logger.info("Start process video")

        frame_id = 0
        batch = []
        while self._abs__has_next_frame():
            try:
                frame = self._abs__next_frame()
                batch.append((frame_id, frame))

                if len(batch) == self.batch_frame_size or not self._abs__has_next_frame():
                    self.thread_pool.submit(self.__process_frame_batch, copy.deepcopy(batch))
                    batch = []

                frame_id += 1
            except Empty:
                continue

        self.done_processing = True
        self.max_frame_count = frame_id

        self.logger.info("End process video. Processed {} frames".format(self.max_frame_count))

    # TODO: synchronize
    def has_next_frame(self):
        return self.max_frame_count > self.current_output_frame

    # TODO: has next/next available
    def next_frame(self):
        while isinstance(self.future_frames[self.current_output_frame % self.max_future_frame_count], int):
            continue

        self.logger.info("Grab processed frame with id {}".format(self.current_output_frame))

        frame = self.future_frames[self.current_output_frame % self.max_future_frame_count]
        self.future_frames[self.current_output_frame % self.max_future_frame_count] = \
            self.current_output_frame + self.max_future_frame_count

        self.current_output_frame += 1

        return frame

    @abstractmethod
    def _abs__join(self):
        pass

    def join(self):
        self._abs__join()

        self.__main_processor_thread.join()
