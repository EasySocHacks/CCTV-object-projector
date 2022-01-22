import math
import time

import cv2

from video.visualizer.common_visualizer import CommonVisualizer


class PreprocessEntireVideoVisualizer(CommonVisualizer):
    def visualize(self):
        while not self.video_processor.done_processing:
            time.sleep(1)

        while self.time_frames.not_empty:
            _, frame = self.time_frames.get()

            cv2.imshow(self.window_name, frame)
            cv2.waitKey(math.ceil(1 / self.fps * 10**3))

        cv2.destroyAllWindows()
