from queue import Queue
from threading import Thread

import cv2

from detector.pool.detector_pool import DetectorPool
from video.processor.common_video_processor import CommonVideoProcessor


class VideoProcessor(CommonVideoProcessor):
    def __init__(self, video_path, skip_frame_count, frame_processor_count, detector_pool: DetectorPool):
        self.video_path = video_path
        self.__video_capture = cv2.VideoCapture(self.video_path)

        self.__frames = Queue()
        self.__collecting_frames_thread = Thread(target=self.__collect_frames)
        self.__collecting_frames_thread.start()
        self.__done = False

        super().__init__(skip_frame_count, frame_processor_count, detector_pool)

        self.__collecting_frames_thread.join()

    def __collect_frames(self):
        while True:
            ok, frame = self.__video_capture.read()
            self.__frames.put(frame)

            if not ok:
                break

        self.__done = True

    def _abs__has_next_frame(self):
        return self.__frames.not_empty or not self.__done

    def _abs__next_frame(self):
        return self.__frames.get()
