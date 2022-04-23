import numpy as np
import torch

from detector.object_class import ObjectClassType


class Projector:
    def __init__(self, config):
        self.config = config

        self._frame_id_projection_dict = {}

        self._previous_projections_dict = {
            ObjectClassType.PERSON.value: np.array([]),
            ObjectClassType.CAR.value: np.array([])
        }

    def append_projection_class_list(self, video_id, frame_id, projection_class_idx_array):
        if frame_id not in self._frame_id_projection_dict:
            self._frame_id_projection_dict[frame_id] = {}

        self._frame_id_projection_dict[frame_id][video_id] = projection_class_idx_array

    def get_json_batch(self):
        result = []
        for frame_id in self._frame_id_projection_dict:
            result.append({
                "frameId": frame_id,
                "points": []
            })

            for video_id in self._frame_id_projection_dict[frame_id]:
                for x, y, _, cls, ind in self._frame_id_projection_dict[frame_id][video_id]:

                    radius = 0.0
                    class_type = ""
                    if cls == ObjectClassType.PERSON.value:
                        radius = self.config.person_radius
                        class_type = "PERSON"

                    if cls == ObjectClassType.CAR.value:
                        radius = self.config.car_radius
                        class_type = "CAR"

                    result[-1]["points"].append({
                        "x": x,
                        "y": y,
                        "radius": radius,
                        "classType": class_type
                    })

        self._frame_id_projection_dict = {}

        torch.multiprocessing.get_logger().debug(
            "Projections:\n{}".format(result)
        )

        return result
