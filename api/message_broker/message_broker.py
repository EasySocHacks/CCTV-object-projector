import asyncio
import json
from logging import getLogger
from threading import Thread, Event

import websockets

from camera import Camera
from main_loop.MainLoop import MainLoop
from video import Video


class MessageBroker:
    def __init__(self, host):
        self.host = host
        self.__logger__ = getLogger()

        self.__camera_video_list__ = []

        self.__working_process__ = Thread(target=self.__run_process__)
        self.__kill_thread_event__ = Event()

        self.main_loop = None

    def start(self):
        self.__logger__.info("Starting MessageBroker")
        self.__working_process__.start()
        self.__logger__.info("MessageBroker started")

    def join(self):
        self.__logger__.info("Joining MessageBroker")
        self.__working_process__.join()
        self.__logger__.info("MessageBroker joined")

    def kill(self):
        self.__logger__.info("Killing MessageBroker")
        self.__kill_thread_event__.set()
        self.__logger__.info("MessageBroker killed")

    def __run_process__(self):
        asyncio.run(self.__work__())

    async def __work__(self):
        async with websockets.connect("ws://{}/backend/websocket".format(self.host)) as websocket:
            self.__logger__.info("Establish websocket connection with frontend")

            while True:
                if self.__kill_thread_event__.is_set():
                    break

                self.__logger__.info("Awaiting command from frontend")

                response_data = await websocket.recv()
                response_json = json.loads(response_data)
                self.__proceed_command__(response_json)

    def __proceed_command__(self, response):
        command = response["command"]
        self.__logger__.info("Processing command '{}', received from frontend".format(command))

        if command == "APPEND_CAMERA_VIDEO":
            video_id = response["id"]
            url = response["url"]

            self.__logger__.info("Appending camera's video with url '{}'".format(url))

            self.__camera_video_list__.append(Video(url, video_id, Camera()))
        elif command == "START_PROCESSING_VIDEO":
            self.main_loop = MainLoop(self.host, self.__camera_video_list__, "cpu")
            self.main_loop.start()
        elif command == "STOP_PROCESSING_VIDEO":
            pass
        elif command == "COMPUTE_CALIBRATION_MATRIX":
            pass
        else:
            self.__logger__.warning("Unknown command '{}', received from frontend".format(command))
