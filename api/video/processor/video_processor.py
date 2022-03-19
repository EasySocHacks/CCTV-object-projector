import cv2
import dlib
from torch.multiprocessing import Queue, Process, get_logger


class VideoProcessor:
    def __init__(self,
                 config,
                 device,
                 processor_linker_queue
                 ):
        self.config = config
        self.device = device
        self.processor_linker_queue = processor_linker_queue

        self.queue = Queue()

        self._detector = self.config.detector_type(device)
        # TODO: None == no expander ?
        self._bbox_expander = self.config.bbox_expander_type(device)

        # self._process = Process(
        #     target=self._process_loop,
        #     args=(
        #         self.process_started,
        #         self.queue,
        #         self.processor_linker_queue,
        #         self.device,
        #         self.config.detector_type,
        #         self.config.bbox_expander_type,
        #     )
        # )

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

            # process_thread = Thread(
            #     target=self._process_batch,
            #     args=(
            #         processor_linker_queue,
            #         video_id,
            #         batch,
            #         detector,
            #         bbox_expander,
            #     )
            # )
            #
            # process_thread.start()
            self._process_batch(
                processor_linker_queue,
                video_id,
                batch
            )

    def _process_batch(self, processor_linker_queue, video_id, batch):
        # expand_list = []
        tracker_class_list = []

        # TODO: Add video_id to incoming batches
        # TODO: Fix current for
        for frame_id, (iteration_id, frame) in enumerate(batch):
            self._logger.debug("Start processing frame with iteration id '{}' for video id '{}' and frame id '{}'"
                               .format(iteration_id, video_id, frame_id))
            bbox_class_list = []

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
                    if obj_class != 0 and obj_class != 2:
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

                    # frame = cv2.rectangle(
                    #     frame,
                    #     (int(obj_bbox[0]), int(obj_bbox[1])),
                    #     (int(obj_bbox[2]), int(obj_bbox[3])),
                    #     (0, 0, 255)
                    # )

                    croped_image = rgb_frame[
                                   int(obj_bbox[1]):int(obj_bbox[3]),
                                   int(obj_bbox[0]):int(obj_bbox[2])
                                   ]

                    # expand = expander.expand(Image.fromarray(croped_image))
                    # expand_bbox = BboxExpander.apply_expand(obj_bbox, expand)

                    # bbox_class_list.append((expand_bbox, obj_class))
                    bbox_class_list.append((obj_bbox, obj_class))

                    # cv2.rectangle(
                    #     frame,
                    #     (int(expand_bbox[0]), int(expand_bbox[1])),
                    #     (int(expand_bbox[2]), int(expand_bbox[3])),
                    #     (255, 0, 0)
                    # )

                    # expand_list.append(expand)
            else:
                # for (tracker, obj_class), expand in zip(tracker_class_list, expand_list):
                #     tracker.update(rgb_frame)
                #     tracker_position = tracker.get_position()
                #
                #     bbox = [
                #         tracker_position.left(),
                #         tracker_position.top(),
                #         tracker_position.right(),
                #         tracker_position.bottom()
                #     ]
                #
                #     expand_bbox = BboxExpander.apply_expand(bbox, expand)
                #
                #     bbox_class_list.append((expand_bbox, obj_class))
                #
                #     cv2.rectangle(
                #         frame,
                #         (int(expand_bbox[0]), int(expand_bbox[1])),
                #         (int(expand_bbox[2]), int(expand_bbox[3])),
                #         (255, 0, 0)
                #     )

                for tracker, obj_class in tracker_class_list:
                    tracker.update(rgb_frame)
                    tracker_position = tracker.get_position()

                    bbox = [
                        tracker_position.left(),
                        tracker_position.top(),
                        tracker_position.right(),
                        tracker_position.bottom()
                    ]

                    # expand_bbox = BboxExpander.apply_expand(bbox, expand)

                    # bbox_class_list.append((expand_bbox, obj_class))
                    bbox_class_list.append((bbox, obj_class))

                    frame = cv2.rectangle(
                        frame,
                        (int(bbox[0]), int(bbox[1])),
                        (int(bbox[2]), int(bbox[3])),
                        (255, 0, 0)
                    )

            processor_linker_queue.put((video_id, iteration_id, frame, bbox_class_list))
            self._logger.debug("Done processing frames with iteration id '{}' for video id '{}'"
                               .format(iteration_id, video_id))
