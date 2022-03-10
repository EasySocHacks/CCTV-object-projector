from exception import EndOfVideoException


class FrameCollector:
    def __init__(self, video):
        self.video = video

    def get_next(self):
        ok, frame = self.video.video_capture.read()

        if not ok:
            raise EndOfVideoException

        return frame
