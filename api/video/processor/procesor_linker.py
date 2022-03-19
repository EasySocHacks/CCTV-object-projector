import json
import subprocess
import tempfile
from threading import Thread

import cv2
import ffmpeg
import requests
from torch.multiprocessing import Process, get_logger, Queue


class ProcessorLinker:
    def __init__(self, config, video_meta):
        self.config = config
        self.video_meta = video_meta

        self.queue = Queue()
        self._linker_process = Process(target=self._link, args=(self.queue, self.video_meta,))

        self._logger = get_logger()

    def start(self):
        self._logger.info("Starting ProcessLinker")
        self._linker_process.start()
        self._logger.info("ProcessLinker started")

    def join(self):
        self._logger.info("Joining ProcessLinker")
        self._linker_process.kill()
        self._logger.info("ProcessLinker joined")

    def kill(self):
        self._logger.info("Killing ProcessLinker")
        self._linker_process.kill()
        self._logger.info("ProcessLinker killed")

    def _convert_and_send(self, sequence_id, batches):
        self._logger.debug("Prepare to send sequence with id '{}'".format(sequence_id))

        for video_id in batches:
            video_batch = batches[video_id]

            fps = int(self.video_meta[video_id]["fps"])
            width = int(self.video_meta[video_id]["width"])
            height = int(self.video_meta[video_id]["height"])

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

                # TODO: change to subprocess
                with tempfile.NamedTemporaryFile(suffix=".ts") as tmp_file_ts:
                    # subprocess.call("ffmpeg -y -i {} -muxdelay 0 -output_ts_offset {} -vcodec copy {}".format(
                    #     tmp_file_mp4.name,
                    #     sequence_id,
                    #     tmp_file_ts.name
                    # ), shell=True)
                    # TODO: different FPS?
                    ffmpeg \
                        .input(tmp_file_mp4.name) \
                        .output(tmp_file_ts.name, vcodec='libx264', acodec='aac', audio_bitrate='160K',
                                vbsf='h264_mp4toannexb', format='mpegts',
                                muxdelay=0,
                                output_ts_offset=str(float(sequence_id * self.config.stride_between_send) / fps)) \
                        .run(capture_stdout=True, capture_stderr=True, quiet=True, overwrite_output=True)

                    duration_format = subprocess.check_output([
                        'ffprobe', '-i', tmp_file_ts.name, '-show_entries', 'format=duration', '-v', 'quiet', '-of',
                        'json'
                    ]).decode('utf8')
                    duration_format_json = json.loads(duration_format)
                    duration = duration_format_json["format"]["duration"]

                    data = tmp_file_ts.read()

                    # TODO: Send whole batch
                    requests.post("{}://{}:{}/api/v{}/video/{}/fragment/{}".format(
                        self.config.method,
                        self.config.host,
                        self.config.port,
                        self.config.api_version,
                        video_id,
                        sequence_id
                    ), data=data,
                        headers={
                            "X-Fragment-duration": str(duration)
                        })

                    tmp_file_ts.close()

                tmp_file_mp4.close()

        self._logger.debug("Sent batch '{}' to frontend".format(sequence_id))

    def _link(self, queue, video_meta):
        processed_dict = {}

        next_sequence_id = 0
        next_iteration_id = 0

        batches = {}
        append_cnt = 0

        while True:
            video_id, iteration_id, frame, bbox_class_list = queue.get()

            if iteration_id not in processed_dict:
                processed_dict[iteration_id] = []

            processed_dict[iteration_id].append((video_id, frame, bbox_class_list))

            if iteration_id == next_iteration_id and len(processed_dict[next_iteration_id]) == len(video_meta):
                self._logger.debug("Start linking iteration id '{}'".format(iteration_id))

                for video_id, frame, bbox_class_list in processed_dict[next_iteration_id]:
                    if video_id not in batches:
                        batches[video_id] = []

                    batches[video_id].append((frame, bbox_class_list))
                    append_cnt += 1

                del processed_dict[next_iteration_id]

                if append_cnt == self.config.stride_between_send * len(video_meta):
                    Thread(target=self._convert_and_send, args=(next_sequence_id, batches,)).start()
                    next_sequence_id += 1

                    batches = {}

                    append_cnt = 0

                next_iteration_id += 1
