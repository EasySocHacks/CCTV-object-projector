import os.path
from queue import Empty

import cv2

from video.processor.common_video_processor import CommonVideoProcessor
from video.visualizer.common_visualizer import CommonVisualizer


class WriteToFileVisualizer(CommonVisualizer):
    def __init__(self, video_saving_folder, video_processor: CommonVideoProcessor, window_name):
        super().__init__(video_processor, window_name)

        self.video_saving_folder = video_saving_folder

    # TODO: use capture params
    def visualize(self):
        video_writer = cv2.VideoWriter(
            os.path.join(self.video_saving_folder, "{}.mp4".format(self.window_name)),
            cv2.VideoWriter_fourcc("m", "p", "4", "v"),
            30.0,
            (1920, 1080)
        )

        # TODO: delete counter
        cnt = 0
        while self.time_frames.qsize() != 0 or self.video_processor.has_next_frame():
            try:
                cnt += 1

                video_writer.write(self.time_frames.get_nowait()[1])
                print("cnt:", cnt)
                self.time_frames.task_done()
            except Empty:
                cnt -= 1
                continue

        video_writer.release()
