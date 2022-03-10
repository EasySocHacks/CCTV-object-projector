from abc import ABC

import cv2
import pafy


class Video(ABC):
    def __init__(self, video_id, camera):
        self.video_id = video_id
        self.camera = camera

        self.video_capture = None


class YouTubeVideo(Video):
    def __init__(self, url, video_id, camera):
        super().__init__(video_id, camera)

        self.url = url

        pafy_url = pafy.new(url)
        play = pafy_url.getbest(preftype="mp4")

        self.capture = cv2.VideoCapture(play.url)
