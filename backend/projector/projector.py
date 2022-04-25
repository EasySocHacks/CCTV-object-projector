import numpy as np

from detector.object_class import ObjectClassType


class Projector:
    def __init__(self, config):
        self.config = config

        self._previous_projections_dict = {}

    @staticmethod
    def _frame_projections_to_points_json(projections, radius, class_type):
        points = []

        for x, y in projections:
            points.append({
                "x": x,
                "y": y,
                "radius": radius,
                "classType": class_type
            })

        return points

    def get_next_projection_batch(self, frame_id_video_id_dict):
        result = []

        for frame_id in frame_id_video_id_dict:
            result.append({
                "frameId": frame_id,
                "points": []
            })

            projections_dict = {}

            for video_id in frame_id_video_id_dict[frame_id]:
                for x, y, _, cls, idx in frame_id_video_id_dict[frame_id][video_id]:
                    r = 0.0
                    if cls == ObjectClassType.PERSON.value:
                        r = self.config.person_radius
                    if cls == ObjectClassType.CAR.value:
                        r = self.config.car_radius

                    if cls not in self._previous_projections_dict:
                        self._previous_projections_dict[cls] = np.array([])

                    if cls not in projections_dict:
                        projections_dict[cls] = {
                            "projections": np.array([]).reshape((0, 5)),
                            "projection_cnt": 0,
                            "radius": r
                        }

                    projections_dict[cls]["projection_cnt"] += 1
                    projections_dict[cls]["projections"] = np.append(
                        projections_dict[cls]["projections"],
                        [[x, y, cls, idx, video_id]],
                        axis=0
                    )

            for cls in projections_dict:
                projections = projections_dict[cls]["projections"]
                projection_cnt = projections_dict[cls]["projection_cnt"]
                radius = projections_dict[cls]["radius"]

                video_id_array = projections[:, 4]

                dist_matrix = np.linalg.norm(
                    np.repeat([projections[:, :2]], projection_cnt, axis=0).reshape((projection_cnt ** 2, 2)) -
                    np.repeat(projections[:, :2], projection_cnt, axis=0),
                    axis=1
                ).reshape((projection_cnt, projection_cnt))

                same_video_id_matrix = (
                        np.repeat([video_id_array], projection_cnt, axis=0).flatten() ==
                        np.repeat(video_id_array, projection_cnt, axis=0)
                ).reshape((projection_cnt, projection_cnt))

                dist_matrix[same_video_id_matrix] = np.inf

                correlations_arg = np.argwhere(dist_matrix <= radius)
                correlations = dist_matrix[correlations_arg[:, 0], correlations_arg[:, 1]]

                if correlations.shape[0] == 0:
                    projections_dict[cls] = {
                        "projections": projections[:, :2],
                        "projection_cnt": projection_cnt,
                        "radius": radius
                    }

                    continue

                correlations = np.vstack([
                    correlations,
                    correlations_arg[:, 0],
                    correlations_arg[:, 1],
                    np.vstack([
                        correlations_arg[:, 0],
                        video_id_array[correlations_arg[:, 1]]
                    ]).T
                ])
                correlations = correlations[:, np.argsort(correlations[0, :])]
                correlations = correlations[:, np.unique(correlations[3, :].astype(np.float64))]
                correlations = correlations[1:-1, :].astype(np.float64)

                correlation_matrix = np.full((projection_cnt, projection_cnt), False)
                correlation_matrix[correlations.T] = True

                correlation_array = np.full(projection_cnt, -1)
                new_projections = np.array([])

                for idx in range(projection_cnt):
                    if correlation_array[idx] == -1:
                        new_projections = np.append(new_projections, projections[idx]).reshape((-1, 2))
                        correlation_array[idx] = new_projections.shape[0] - 1

                    correlation_j_array = np.arange(0, projection_cnt)[correlation_matrix[idx, :]]

                    for j in correlation_j_array:
                        if correlation_array[j] == -1:
                            new_projections[correlation_array[idx]] = np.mean([
                                new_projections[correlation_array[idx]],
                                projections[j]
                            ], axis=0)
                            correlation_array[j] = correlation_array[idx]

                projections_dict[cls] = {
                    "projections": new_projections,
                    "projection_cnt": new_projections.shape[0],
                    "radius": radius
                }

            for cls in projections_dict:
                radius = projections_dict[cls]["radius"]
                class_type = None
                if cls == ObjectClassType.PERSON.value:
                    class_type = "PERSON"
                if cls == ObjectClassType.CAR.value:
                    class_type = "CAR"

                if cls not in self._previous_projections_dict or self._previous_projections_dict[cls].shape[0] == 0:
                    self._previous_projections_dict[cls] = projections_dict[cls]["projections"]

                    result[-1]["points"].extend(self._frame_projections_to_points_json(
                        projections_dict[cls]["projections"],
                        radius,
                        class_type
                    ))
                else:
                    previous_projections = self._previous_projections_dict[cls]
                    previous_projection_cnt = previous_projections.shape[0]

                    projections = projections_dict[cls]["projections"]
                    projection_cnt = projections_dict[cls]["projection_cnt"]

                    if cls == ObjectClassType.PERSON.value:
                        mean_distance_per_frame = self.config.person_mean_distance_per_frame()
                    if cls == ObjectClassType.CAR.value:
                        mean_distance_per_frame = self.config.car_mean_distance_per_frame()
                    else:
                        mean_distance_per_frame = 0.0

                    dist_matrix = np.linalg.norm(
                        np.repeat([previous_projections], projection_cnt, axis=0).reshape(
                            (previous_projection_cnt * projection_cnt, 2)) -
                        np.repeat(projections, previous_projection_cnt, axis=0),
                        axis=1
                    ).reshape((projection_cnt, previous_projection_cnt))

                    where_correlation_arg = np.argwhere(dist_matrix <= mean_distance_per_frame)

                    if where_correlation_arg.shape[0] == 0:
                        self._previous_projections_dict[cls] = projections

                        result[-1]["points"].extend(self._frame_projections_to_points_json(
                            projections,
                            radius,
                            class_type
                        ))

                        continue

                    correlations = np.vstack([
                        dist_matrix[where_correlation_arg[:, 0], where_correlation_arg[:, 1]],
                        where_correlation_arg.T
                    ])

                    correlations = correlations[:, np.argsort(correlations[0, :])]
                    correlations = correlations[1:, :]
                    correlations = correlations.astype(np.int64)

                    correlation_matrix = np.full((projection_cnt, previous_projection_cnt), False)

                    for i, j in correlations.T:
                        if np.ma.any(correlation_matrix[i, :]) or np.ma.any(correlation_matrix[:, j]):
                            continue

                        correlation_matrix[i, j] = True

                    projections_correlations = np.stack([projections, projections], axis=1)
                    where_correlation_arg = np.argwhere(correlation_matrix)
                    projections_correlations[where_correlation_arg[:, 0], 1, :] = \
                        previous_projections[where_correlation_arg[:, 1], :]

                    new_projections = np.mean(projections_correlations, axis=1)
                    self._previous_projections_dict[cls] = new_projections

                    result[-1]["points"].extend(
                        self._frame_projections_to_points_json(new_projections, radius, class_type)
                    )

        return result