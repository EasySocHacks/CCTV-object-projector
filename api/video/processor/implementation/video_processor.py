from queue import Queue
from threading import Thread

import cv2

from bbox_expander.bbox_expander import BboxExpander
from detector.pool.detector_pool import DetectorPool
from video.processor.common_video_processor import CommonVideoProcessor


class VideoProcessor(CommonVideoProcessor):
    def __init__(self,
                 video_path,
                 skip_frame_count,
                 frame_processor_count,
                 detector_pool: DetectorPool,
                 bbox_expander: BboxExpander):
        self.video_path = video_path
        self.__video_capture = cv2.VideoCapture(self.video_path)

        self.__frames = Queue()
        self.__collecting_frames_thread = Thread(target=self.__collect_frames)

        self.collecting = True

        super().__init__(skip_frame_count, frame_processor_count, detector_pool, bbox_expander)

    def _abs__process(self):
        self.__collecting_frames_thread.start()

    def __collect_frames(self):
        while True:
            ok, frame = self.__video_capture.read()

            if not ok:
                break

            self.__frames.put(frame)

        self.__video_capture.release()

        self.collecting = False

    def _abs__has_next_frame(self):
        return self.__frames.qsize() != 0 or self.collecting

    def _abs__next_frame(self):
        frame = self.__frames.get_nowait()

        self.__frames.task_done()

        return frame

    def _abs__join(self):
        self.__collecting_frames_thread.join()
        self.__frames.join()
