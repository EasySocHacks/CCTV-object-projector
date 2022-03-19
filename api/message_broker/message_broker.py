import asyncio
import json
from multiprocessing import get_logger
from threading import Event

import websockets

from camera import Camera
from main_loop import MainLoop
from video import YouTubeVideo


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

        if command == "APPEND_CAMERA_VIDEO":
            video_id = response["id"]
            # TODO: change to 'uri'
            uri = response["url"]

            self._logger.info("Appending camera's video with uri '{}'".format(uri))

            # TODO: camera/file video
            self._main_loop.append_video(YouTubeVideo(uri, video_id, Camera()))
        elif command == "START_PROCESSING_VIDEO":
            self._main_loop.start()
        elif command == "COMPUTE_CALIBRATION_MATRIX":
            pass
        else:
            self._logger.warning("Unknown command '{}', received from frontend".format(command))
