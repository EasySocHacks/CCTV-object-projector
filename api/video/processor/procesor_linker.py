import json
import subprocess
import tempfile
from logging import getLogger
from threading import Thread, Event

import cv2
import ffmpeg
import requests


class ProcessorLinker:
    def __init__(self, host, video_list, send_frame_batch_size=50):
        self.host = host
        self.video_list = video_list
        self.send_frame_batch_size = send_frame_batch_size

        self.__processed_dict__ = {}

        self.__linker_process__ = Thread(target=self.__link__)
        self.__kill_thread_event__ = Event()

        self.__logger__ = getLogger()

    def start(self):
        self.__logger__.info("Starting ProcessLinker")
        self.__linker_process__.start()
        self.__logger__.info("ProcessLinker started")

    def kill(self):
        self.__logger__.info("Killing ProcessLinker")
        self.__kill_thread_event__.set()
        self.__logger__.info("ProcessLinker killed")

    def append_processed(self, video_id, iteration_id, frame, bbox_class_list):
        if iteration_id not in self.__processed_dict__:
            self.__processed_dict__[iteration_id] = []

        self.__processed_dict__[iteration_id].append((video_id, frame, bbox_class_list))

    def __send__(self, sequence_id, batch):
        self.__logger__.debug("Prepare to send sequence with id '{}'".format(sequence_id))

        for video_id, video_batch in enumerate(batch):
            fps = self.video_list[video_id].video_capture.get(cv2.CAP_PROP_FPS)
            width = self.video_list[video_id].video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.video_list[video_id].video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

            with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp_file_mp4:
                writer = cv2.VideoWriter(
                    tmp_file_mp4.name,
                    cv2.VideoWriter_fourcc(*"mp4v"),
                    fps,
                    (width, height)
                )

                for frame, bbox_clas_list in video_batch:
                    writer.write(frame)

                writer.release()

                with tempfile.NamedTemporaryFile(suffix=".ts") as tmp_file_ts:
                    ffmpeg \
                        .input(tmp_file_mp4.name) \
                        .output(tmp_file_ts.name, vcodec='libx264', acodec='aac', audio_bitrate='160K',
                                vbsf='h264_mp4toannexb', format='mpegts',
                                muxdelay=str(float(sequence_id * self.send_frame_batch_size) / fps)) \
                        .run(capture_stdout=True, capture_stderr=True, quiet=True, overwrite_output=True)

                    duration_format = subprocess.check_output([
                        'ffprobe', '-i', tmp_file_ts.name, '-show_entries', 'format=duration', '-v', 'quiet', '-of',
                        'json'
                    ]).decode('utf8')
                    duration_format_json = json.loads(duration_format)
                    duration = duration_format_json["format"]["duration"]

                    data = tmp_file_ts.read()

                    # TODO: Send whole batch
                    # TODO: http/https
                    requests.post("http://{}/video/{}/fragment/{}".format(
                        self.host,
                        self.video_list[video_id].video_id,
                        sequence_id
                    ), data=data,
                        headers={
                            "X-Fragment-duration": str(duration)
                        })

                    tmp_file_ts.close()

                tmp_file_mp4.close()

        self.__logger__.info("Sent batch '{}' to frontend".format(sequence_id))

    def __link__(self):
        iteration_id = 0

        batch = [[]] * self.send_frame_batch_size

        while True:
            self.__logger__.debug("Start linking iteration id '{}'".format(iteration_id))

            if iteration_id in self.__processed_dict__ and \
                    len(self.__processed_dict__[iteration_id]) >= len(self.video_list):
                for video_id, frame, bbox_class_list in self.__processed_dict__[iteration_id]:
                    batch[video_id].append((frame, bbox_class_list))

            if len(batch[0]) >= self.send_frame_batch_size:
                Thread(target=self.__send__, args=(iteration_id / self.send_frame_batch_size, batch,)).start()
                batch = [[] * self.send_frame_batch_size]

            iteration_id += 1
