import time
from abc import ABC, abstractmethod
from queue import Queue
from threading import Thread

from video.processor.common_video_processor import CommonVideoProcessor


class CommonVisualizer(ABC):
    def __init__(self, video_processor: CommonVideoProcessor, window_name, fps=30):
        self.video_processor = video_processor
        self.window_name = window_name
        self.fps = fps

        self.time_frames = Queue()

        self.collector_thread = Thread(target=self.__collect_frames)
        self.collector_thread.start()

    def __collect_frames(self):
        while self.video_processor.has_next_frame():
            try:
                self.time_frames.put((time.time_ns(), self.video_processor.next_frame()))
            except Exception:
                continue

        self.video_processor.join()

    @abstractmethod
    def visualize(self):
        pass
