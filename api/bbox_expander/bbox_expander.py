import torch
from torchvision import transforms

from bbox_expander.bbox_expand_net import BboxExpandNet


class BboxExpander:
    def __init__(self):
        self.data_transforms = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        self.device = torch.device("cuda:3" if torch.cuda.is_available() else "cpu")

        self.weight_path = "data/bbox_expander/weight/model_final.pth"

        self.model = BboxExpandNet()
        self.model.to(self.device)
        self.model.load_state_dict(torch.load(self.weight_path, map_location=torch.device(self.device)))
        self.model.eval()

    def expand(self, image, bbox):
        x = bbox[0]
        y = bbox[1]
        w = bbox[2] - x
        h = bbox[3] - y
        x += w / 2.0
        y += h / 2.0

        out = self.model(self.data_transforms(image).unsqueeze(0).to(self.device)).tolist()[0]
        print(out)

        nw = w / out[0]
        nh = h / out[1]
        nx = out[2] * (nw / 2.0) + x
        ny = out[3] * (nh / 2.0) + y

        return [nx - nw / 2.0, ny - nh / 2.0, nx + nw / 2.0, ny + nh / 2.0]
