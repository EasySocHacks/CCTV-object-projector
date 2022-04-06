import torch

from detector import Detector


class YoloDetector(Detector):
    def __init__(self, device, yolo_version):
        super().__init__(device)

        self.yolo_version = yolo_version
        self.model = torch.hub.load('ultralytics/yolov5', self.yolo_version, pretrained=True)
        self.model.to(device)
        self.model.share_memory()
        self.model.eval()

    def detect(self, image):
        output = self.model(image)
        df = output.pandas().xyxy[0]

        classes = df.loc[:, "class"].to_numpy()
        scores = df.loc[:, "confidence"].to_numpy()
        bboxes = df.iloc[:, 0:4].to_numpy()

        return bboxes, classes, scores

    @staticmethod
    def decode_class(class_id: int):
        pass


class YoloDetectorN(YoloDetector):
    def __init__(self, device):
        super().__init__(device, "yolov5n")


class YoloDetectorS(YoloDetector):
    def __init__(self, device):
        super().__init__(device, "yolov5s")


class YoloDetectorM(YoloDetector):
    def __init__(self, device):
        super().__init__(device, "yolov5m")


class YoloDetectorL(YoloDetector):
    def __init__(self, device):
        super().__init__(device, "yolov5l")


class YoloDetectorX(YoloDetector):
    def __init__(self, device):
        super().__init__(device, "yolov5x")
