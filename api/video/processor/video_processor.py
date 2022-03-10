from multiprocessing import get_logger
from threading import Thread

import cv2
import dlib
from PIL import Image

from bbox_expander.bbox_expander import BboxExpander


class VideoProcessor:
    def __init__(self,
                 video,
                 processor_linker,
                 detector,
                 expander,
                 detect_frame_batch_size=10,
                 detection_threshold=0.6
                 ):
        self.video = video
        self.processor_linker = processor_linker
        self.detector = detector
        self.expander = expander
        self.detect_frame_batch_size = detect_frame_batch_size
        self.detection_threshold = detection_threshold

        self.__logger__ = get_logger()

    def process_batch(self, batch):
        thread = Thread(target=self.__process_batch__, args=(batch,))
        thread.start()

        return thread

    def __process_batch__(self, batch):
        expand_list = []
        tracker_class_list = []

        for frame_id, (iteration_id, frame) in enumerate(batch):
            bbox_class_list = []

            if frame is None:
                self.__logger__.info("VideoProcessor for video id '{}' process dummy None frame on iteration id '{}'"
                                     .format(self.video.video_id, iteration_id))
                self.processor_linker.append_processed(self.video.video_id, iteration_id, None, None)
                continue

            self.__logger__.info("VideoProcessor for video id '{}' processing frame with iteration id '{}'"
                                 .format(self.video.video_id, iteration_id))

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if frame_id % self.detect_frame_batch_size == 0:
                self.__logger__.info("VideoProcessor for video id '{}' starting detection on iteration id '{}'"
                                     .format(self.video.video_id, iteration_id))
                bboxes, classes, scores = self.detector.detect(frame)
                self.__logger__.info("VideoProcessor for vido id '{}' done detection on iteration id '{}'"
                                     .format(self.video.video_id, iteration_id))

                for obj_bbox, obj_class, obj_score in zip(bboxes, classes, scores):
                    # TODO: OOP?
                    if obj_class == 0:
                        continue

                    if obj_score < self.detection_threshold:
                        continue

                    tracker_class_list.append((dlib.correlation_tracker(), obj_class))
                    tracker_class_list[-1][0].start_track(
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

                    expand = self.expander.expand(Image.fromarray(croped_image))
                    expand_bbox = BboxExpander.apply_expand(obj_bbox, expand)

                    bbox_class_list.append((expand_bbox, obj_class))

                    cv2.rectangle(
                        frame,
                        (int(expand_bbox[0]), int(expand_bbox[1])),
                        (int(expand_bbox[2]), int(expand_bbox[3])),
                        (255, 0, 0)
                    )

                    expand_list.append(expand)
            else:
                for (tracker, obj_class), expand in zip(tracker_class_list, expand_list):
                    tracker.update(rgb_frame)
                    tracker_position = tracker.get_position()

                    bbox = [
                        tracker_position.left(),
                        tracker_position.top(),
                        tracker_position.right(),
                        tracker_position.bottom()
                    ]

                    expand_bbox = BboxExpander.apply_expand(bbox, expand)

                    bbox_class_list.append((expand_bbox, obj_class))

                    cv2.rectangle(
                        frame,
                        (int(expand_bbox[0]), int(expand_bbox[1])),
                        (int(expand_bbox[2]), int(expand_bbox[3])),
                        (255, 0, 0)
                    )

            self.processor_linker.append_processed(self.video.video_id, iteration_id, frame, bbox_class_list)
            self.__logger__.info("VideoProcessor for video id '{}' done processing iteration id '{}'"
                                 .format(self.video.video_id, iteration_id))
