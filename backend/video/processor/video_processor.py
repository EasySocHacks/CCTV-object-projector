import cv2
import dlib
import numpy as np
from PIL import Image
from torch.multiprocessing import Queue, Process, get_logger

from bbox_expander import BboxExpander
from detector.object_class.object_class_type import ObjectClassType


class VideoProcessor:
    def __init__(self,
                 config,
                 device,
                 processor_linker_queue,
                 video_dict
                 ):
        self.config = config
        self.device = device
        self.processor_linker_queue = processor_linker_queue
        self.video_dict = video_dict

        self.queue = Queue()

        self._detector = self.config.detector_type(device)
        if self.config.bbox_expander_type is None:
            self._bbox_expander = None
        else:
            self._bbox_expander = self.config.bbox_expander_type(device)

        self._logger = get_logger()

    def generate_process(self):
        self._logger.info("Generating VideoProcessor")

        process = Process(
            target=self._process_loop,
            args=(
                self.queue,
                self.processor_linker_queue,
            )
        )

        self._logger.info("VideoProcessor generated")

        return process

    def _process_loop(self,
                      queue,
                      processor_linker_queue):
        while True:
            # TODO: None == break?
            # TODO: timeout == break?
            data = queue.get()

            if data is None:
                break

            video_id, batch = data

            self._process_batch(
                processor_linker_queue,
                video_id,
                batch
            )

    def _process_batch(self, processor_linker_queue, video_id, batch):
        expand_list = []
        tracker_class_list = []

        for frame_id, (iteration_id, frame) in enumerate(batch):
            self._logger.debug("Start processing frame with iteration id '{}' for video id '{}' and frame id '{}'"
                               .format(iteration_id, video_id, frame_id))
            projection_class_list = []

            if frame is None:
                self._logger.debug("Processed dummy frame with iteration id '{}' for video id '{}'"
                                   .format(iteration_id, video_id))
                processor_linker_queue.put((video_id, iteration_id, None, None))
                continue

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if frame_id == 0:
                self._logger.debug(
                    "Starting detection for frame with iteration id '{}' and frame if '{}' for video id '{}'"
                        .format(iteration_id, frame_id, video_id)
                )
                bboxes, classes, scores = self._detector.detect(frame)
                self._logger.debug(
                    "Done detection for frame with iteration id '{}' and frame id '{}' for video id '{}'"
                        .format(iteration_id, frame_id, video_id)
                )

                for obj_bbox, obj_class, obj_score in zip(bboxes, classes, scores):
                    # TODO: OOP?
                    if obj_class != ObjectClassType.PERSON.value and obj_class != ObjectClassType.CAR.value:
                        continue

                    if obj_score < self.config.detection_threshold:
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

                    croped_image = rgb_frame[
                                   int(obj_bbox[1]):int(obj_bbox[3]),
                                   int(obj_bbox[0]):int(obj_bbox[2])
                                   ]

                    if self._bbox_expander is not None:
                        expand = self._bbox_expander.expand(Image.fromarray(croped_image))
                        expand_bbox = BboxExpander.apply_expand(obj_bbox, expand)

                        final_bbox = expand_bbox

                        expand_list.append(expand)
                    else:
                        final_bbox = obj_bbox

                        expand_list.append(None)

                    if self.video_dict[video_id].camera.calibration is not None:
                        projection = self.video_dict[video_id].camera.calibration.project_2d_to_3d_homo(
                            np.array([(final_bbox[2] + final_bbox[0]) / 2.0, final_bbox[3]])
                        )
                        projection_class_list.append((projection, obj_class))
                    else:
                        projection_class_list.append((None, obj_class))
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

                    if self._bbox_expander:
                        expand_bbox = BboxExpander.apply_expand(bbox, expand)

                        final_bbox = expand_bbox
                    else:
                        final_bbox = bbox

                    if self.video_dict[video_id].camera.calibration is not None:
                        projection = self.video_dict[video_id].camera.calibration.project_2d_to_3d_homo(
                            np.array([(final_bbox[2] + final_bbox[0]) / 2.0, final_bbox[3]])
                        )
                        projection_class_list.append((projection, obj_class))
                    else:
                        projection_class_list.append((None, obj_class))
            processor_linker_queue.put((video_id, iteration_id, frame, projection_class_list))
            self._logger.debug("Done processing frames with iteration id '{}' for video id '{}'"
                               .format(iteration_id, video_id))
