import cv2
from IPython.display import display, Image

from video.visualizer.common_visualizer import CommonVisualizer


class IPythonVisualizer(CommonVisualizer):
    def visualize(self):
        display_handle = display(None, display_id=True)

        while self.time_frames.not_empty or self.video_processor.has_next_frame():
            _, frame = self.time_frames.get()

            frame = cv2.resize(frame, (600, 400))
            _, frame = cv2.imencode('.jpeg', frame)
            display_handle.update(Image(data=frame.tobytes()))
            cv2.waitKey(int(1000 / self.fps))

        display_handle.update(None)
