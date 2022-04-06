import torch
import torchvision

from detector import Detector


class FasterRCNNDetector(Detector):
    def __init__(self, device):
        super().__init__(device)

        self.device = device

        self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
        self.model.requires_grad = False
        self.model.to(self.device)
        self.model.share_memory()
        self.model.eval()

    def detect(self, image):
        tensor = torch.unsqueeze(torchvision.transforms.ToTensor()(image), 0).to(self.device)
        output = self.model(tensor)[0]

        classes = output["labels"].detach().cpu()
        bboxes = output["boxes"].detach().cpu()
        scores = output["scores"].detach().cpu()

        return bboxes, classes, scores

    @staticmethod
    def decode_class(class_id: int):
        pass
