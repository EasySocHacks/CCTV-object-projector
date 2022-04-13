from torch.multiprocessing import get_logger


class Config:
    def __init__(self):
        self._logger = get_logger()

        self.method = "http"

        self.host = "localhost"

        self.port = 4000

        self.token = None

        self.api_version = "1"

        self.stride_between_detection = 10

        self.stride_between_send = 60

        self.available_devices = ["cuda:0"]

        self.detector_type = None

        self.detection_threshold = 0.65

        self.bbox_expander_type = None

        self.screenshot_stride = 1800

        self.fps = 30

        self.person_radius = 0.2

        self.car_radius = 0.75

        self.save_file_video_dir = "data/video"

        self.video_processor_count = 1

    def assert_correct(self):
        if self.stride_between_send % self.stride_between_detection != 0:
            self._logger.error("'stride_between_send' must be dividable by 'stride_between_detection'")
            raise Exception()
