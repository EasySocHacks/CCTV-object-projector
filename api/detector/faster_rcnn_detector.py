import torchvision
from torch.nn.parallel import DistributedDataParallel

from detector import Detector


class FasterRCNNDetector(Detector):
    def __init__(self, device):
        super().__init__(device)

        self.device = device

        self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
        self.model = DistributedDataParallel(self.model)
        self.model.eval()
        self.model.to(self.device)

    def detect(self, image):
        output = self.model(image)[0]

        classes = output["labels"].cpu().numpy()
        bboxes = output["boxes"].cpu().numpy()
        scores = output["scores"].cpu().numpy()

        return bboxes, classes, scores

    @staticmethod
    def decode_class(class_id: int):
        pass
