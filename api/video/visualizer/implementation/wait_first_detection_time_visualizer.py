import math
import time

import cv2

from video.visualizer.common_visualizer import CommonVisualizer


class WaitFirstDetectionTimeVisualizer(CommonVisualizer):
    def visualize(self):
        while self.time_frames.qsize() <= 2 * self.video_processor.skip_frame_count:
            time.sleep(1)

        start_time, frame = self.time_frames.get()
        spf = (time.time_ns() - start_time) / 10**9 / self.time_frames.qsize()
        awaiting_frame_count = spf * self.video_processor.skip_frame_count * self.fps

        while self.time_frames.qsize() < awaiting_frame_count:
            time.sleep(1)

        while self.time_frames.not_empty or self.video_processor.has_next_frame():
            _, frame = self.time_frames.get()

            cv2.imshow(self.window_name, frame)
            cv2.waitKey(math.ceil(1 / self.fps * 10**3))

        cv2.destroyAllWindows()
