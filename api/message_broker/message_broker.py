import asyncio
import json
from multiprocessing import get_logger
from threading import Event

import numpy as np
import websockets

from camera import Camera
from camera.calibration.calibration import Calibration
from main_loop import MainLoop
from video.video import Video


class MessageBroker:
    def __init__(self, config):
        self.config = config
        self._logger = get_logger()

        self._kill_thread_event = Event()

        self._main_loop = MainLoop(config)

    def start(self):
        self._logger.info("Starting MessageBroker")

        asyncio.run(self._work())
        self._logger.info("MessageBroker started")

    def kill(self):
        self._logger.info("Killing MessageBroker")
        self._kill_thread_event.set()
        self._logger.info("MessageBroker killed")

    async def _work(self):
        async with websockets.connect(
                "ws://{}:{}/backend/websocket".format(self.config.host, self.config.port)
        ) as websocket:
            self._logger.info("Establish websocket connection with frontend")

            while True:
                if self._kill_thread_event.is_set():
                    break

                self._logger.info("Awaiting command from frontend")

                response_data = await websocket.recv()
                response_json = json.loads(response_data)
                self._proceed_command(response_json)

    def _proceed_command(self, response):
        command = response["command"]
        self._logger.info("Processing command '{}', received from frontend".format(command))

        if command == "START_SESSION":
            session_id = response["sessionId"]

            self._main_loop.session_id = session_id
        elif command == "APPEND_VIDEO":
            video_id = response["videoId"]
            uri = response["uri"]
            streaming_type = response["streamingType"]

            self._logger.info("Appending camera's video with uri '{}'".format(uri))

            self._main_loop.append_video(
                Video(
                    video_id,
                    self._main_loop.session_id,
                    uri,
                    streaming_type,
                    Camera()
                )
            )
        elif command == "START_STREAMING":
            self._main_loop.start()
        elif command == "SET_CALIBRATION":
            video_id = response["videoId"]
            points = response["calibrationPointList"]

            screen_points = np.array([])
            world_points = np.array([])
            for point in points:
                x_screen = point["xScreen"]
                y_screen = point["yScreen"]

                screen_points = np.append(screen_points, [x_screen, y_screen])

                x_word = point["xWorld"]
                y_word = point["yWorld"]
                z_word = point["zWorld"]

                world_points = np.append(world_points, [x_word, y_word, z_word])

            screen_points = screen_points.reshape((6, 2))
            world_points = world_points.reshape((6, 3))

            calibration = Calibration(screen_points, world_points)
            self._logger.debug("Calibration set to video with id '{}' with matrix\n{}\nAnd camera position\n{}".format(
                video_id,
                calibration.matrix,
                calibration.camera_coordinates
            ))
            self._main_loop.video_dict[video_id].camera.calibration = calibration
        else:
            self._logger.warning("Unknown command '{}', received from frontend".format(command))
