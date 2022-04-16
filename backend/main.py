import argparse
from logging import INFO

import torch
from torch.multiprocessing import log_to_stderr, set_start_method

from bbox_expander import BboxExpander
from config import Config
from detector import YoloDetector
from detector.detectron2_detector import Detectron2Detector
from message_broker import MessageBroker


def main():
    set_start_method("spawn", True)
    log_to_stderr(INFO)

    torch.hub.set_dir("data/torch/hub")

    config = Config()

    argument_parser = argparse.ArgumentParser(description="Starting a backend for CCTV-Object-Projection")
    argument_parser.add_argument(
        "--host",
        "-H",
        metavar="host",
        type=str,
        required=True,
        help="set frontend host value to connect"
    )
    argument_parser.add_argument(
        "--port",
        "-P",
        metavar="port",
        type=int,
        required=True,
        help="set frontend port value to connect"
    )
    argument_parser.add_argument(
        "--secure",
        "-S",
        action="store_true",
        required=False,
        help="enable secure message protocol (https & wss)"
    )
    argument_parser.add_argument(
        "--api",
        metavar="version",
        type=str,
        default=config.api_version,
        required=False,
        help="set frontend api version"
    )
    argument_parser.add_argument(
        "--stride_detection",
        metavar="stride",
        type=int,
        default=config.stride_between_detection,
        required=False,
        help="set stride value in frames of detection apply for each video stream"
    )
    argument_parser.add_argument(
        "--stride_send",
        metavar="stride",
        type=int,
        default=config.stride_between_send,
        required=False,
        help="set stride value in frames of sending batch to frontend"
    )
    argument_parser.add_argument(
        "--devices",
        metavar="device",
        type=str,
        nargs="+",
        default=config.available_devices,
        required=False,
        help=
        "list devices to work with. Devices must me either 'cpu' or 'cuda:x', where 'x' is number of gpu to work with"
    )
    argument_parser.add_argument(
        "--detector",
        metavar="detector",
        type=str,
        action="store",
        choices=[
            "yolov5n",
            "yolov5s",
            "yolov5m",
            "yolov5l",
            "yolov5x",

            "fast_rcnn_R_50_FPN_1x",
            "faster_rcnn_R_101_C4_3x",
            "faster_rcnn_R_101_DC5_3x",
            "faster_rcnn_R_101_FPN_3x",
            "faster_rcnn_R_50_C4_1x",
            "faster_rcnn_R_50_C4_3x",
            "faster_rcnn_R_50_DC5_1x",
            "faster_rcnn_R_50_DC5_3x",
            "faster_rcnn_R_50_FPN_1x",
            "faster_rcnn_R_50_FPN_3x",
            "faster_rcnn_X_101_32x8d_FPN_3x",
            "fcos_R_50_FPN_1x",
            "retinanet_R_101_FPN_3x",
            "retinanet_R_50_FPN_1x",
            "retinanet_R_50_FPN_3x",
            "rpn_R_50_C4_1x",
            "rpn_R_50_FPN_1x",

            "mask_rcnn_R_101_C4_3x",
            "mask_rcnn_R_101_DC5_3x",
            "mask_rcnn_R_101_FPN_3x",
            "mask_rcnn_R_50_C4_1x",
            "mask_rcnn_R_50_C4_3x",
            "mask_rcnn_R_50_DC5_1x",
            "mask_rcnn_R_50_DC5_3x",
            "mask_rcnn_R_50_FPN_1x",
            "mask_rcnn_R_50_FPN_1x_giou",
            "mask_rcnn_R_50_FPN_3x",
            "mask_rcnn_X_101_32x8d_FPN_3x",
        ],
        required=True,
        help="choose a model for detection"
    )
    argument_parser.add_argument(
        "--detector_weights",
        metavar="path",
        type=str,
        default=None,
        required=False,
        help="set custom detector's model weights"
    )
    argument_parser.add_argument(
        "--detector_threshold",
        metavar="threshold",
        type=float,
        default=config.detector_threshold,
        required=False,
        help="set detector threshold"
    )
    argument_parser.add_argument(
        "--bbox_expander",
        "--expander",
        action="append_const",
        const=BboxExpander,
        default=None,
        required=False,
        help="enable BBoxExpander model"
    )
    argument_parser.add_argument(
        "--bbox_expander_weights",
        "--expander_weights",
        metavar="path",
        type=str,
        default=config.bbox_expander_weight_path,
        required=False,
        help="set custom BBoxExpander weights"
    )
    argument_parser.add_argument(
        "--fps",
        metavar="fps",
        type=int,
        default=config.fps,
        required=False,
        help="set sending to frontend fragment's output fps"
    )
    argument_parser.add_argument(
        "--person_radius",
        metavar="radius",
        type=float,
        default=config.person_radius,
        required=False,
        help="set projection radius for detected persons"
    )
    argument_parser.add_argument(
        "--car_radius",
        metavar="radius",
        type=float,
        default=config.car_radius,
        required=False,
        help="set projection radius for detected cars"
    )
    argument_parser.add_argument(
        "--download",
        metavar="path",
        type=str,
        default=config.save_file_video_dir,
        required=False,
        help="set a folder to download file videos to"
    )
    argument_parser.add_argument(
        "--processes",
        metavar="count",
        type=int,
        default=config.video_processor_count,
        required=False,
        help="set number of processes which will be processing videos"
    )

    args = argument_parser.parse_args()

    config.host = args.host
    config.port = args.port
    config.secure = args.secure
    config.api_version = args.api
    config.stride_between_detection = args.stride_detection
    config.stride_between_send = args.stride_send
    config.available_devices = args.devices
    config.detector_weight_path = args.detector_weights
    if args.detector.startswith("yolov5"):
        config.detector_type = YoloDetector.model_from_str(args.detector, config.detector_weight_path)
    else:
        config.detector_type = Detectron2Detector.model_from_str(args.detector, config.detector_weight_path)
    config.detector_threshold = args.detector_threshold
    config.bbox_expander_weight_path = args.bbox_expander_weights
    if args.bbox_expander is not None:
        config.bbox_expander_type = BboxExpander.get_model(config.bbox_expander_weight_path)
    else:
        config.bbox_expander_type = None
    config.fps = args.fps
    config.person_radius = args.person_radius
    config.car_radius = args.car_radius
    config.save_file_video_dir = args.download
    config.video_processor_count = args.processes

    message_broker = MessageBroker(config)
    message_broker.start()


if __name__ == "__main__":
    main()
