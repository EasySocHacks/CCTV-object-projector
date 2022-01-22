import math
import time

import cv2

from video.visualizer.common_visualizer import CommonVisualizer


class DynamicFPSVisualizer(CommonVisualizer):
    def visualize(self):
        spf = 1 / self.fps

        start_batch_time = time.time_ns()

        frame_id = 0
        while self.time_frames.not_empty or self.video_processor.has_next_frame():
            frame_id += 1
            if frame_id % self.video_processor.skip_frame_count == 0:
                end_batch_time = time.time_ns()
                spf = (end_batch_time - start_batch_time) / 10**9 / self.video_processor.skip_frame_count
                start_batch_time = time.time_ns()

            _, frame = self.time_frames.get()

            cv2.imshow(self.window_name, frame)
            cv2.waitKey(math.ceil(spf * 10**3))

        cv2.destroyAllWindows()
