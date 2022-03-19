class Config:
    def __init__(self):
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
