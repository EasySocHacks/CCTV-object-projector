from logging import getLogger
from threading import Thread, Event

from bbox_expander.bbox_expander import BboxExpander
from detector.implementation import Detectron2Detector
from exception import EndOfVideoException
from video.frame_collector.frame_collector import FrameCollector
from video.processor.procesor_linker import ProcessorLinker
from video.processor.video_processor import VideoProcessor


class MainLoop:
    def __init__(self, host, video_list, device, detect_frame_batch_size=10):
        self.host = host
        self.video_list = video_list
        self.device = device
        self.detect_frame_batch_size = detect_frame_batch_size

        self.__iteration_id__ = 0

        self.__processor_linker__ = ProcessorLinker(host, video_list)

        self.__frame_collector_list__ = []
        self.__video_processor_list__ = []

        self.__detector__ = Detectron2Detector(device)
        self.__expander__ = BboxExpander(device)

        for video in video_list:
            self.__frame_collector_list__.append(FrameCollector(video))
            self.__video_processor_list__.append(VideoProcessor(
                video,
                self.__processor_linker__,
                self.__detector__,
                self.__expander__,
                detect_frame_batch_size
            ))

        self.__main_loop_thread__ = Thread(target=self.__loop__)
        self.__kill_thread_event__ = Event()

        self.__logger__ = getLogger()

    def start(self):
        self.__logger__.info("Starting MainLoop")
        self.__processor_linker__.start()

        self.__main_loop_thread__.start()
        self.__logger__.info("MainLoop started")

    def kill(self):
        self.__logger__.info("Killing MainLoop")
        self.__kill_thread_event__.set()

        self.__processor_linker__.kill()
        self.__logger__.info("MainLoop killed")

    def __loop__(self):
        self.__logger__.info("MainLoop start collecting frames")

        batch = [[]] * len(self.video_list)

        while True:
            if self.__kill_thread_event__.is_set():
                break

            self.__logger__.info("MainLoop collecting frames with iteration id '{}'".format(self.__iteration_id__))
            progress = False

            # TODO: using vido.video_id
            for video_id, frame_collector in enumerate(self.__frame_collector_list__):
                try:
                    frame = frame_collector.get_next()

                    # TODO: using dict {}
                    batch[video_id].append((self.__iteration_id__, frame))

                    progress = True
                except EndOfVideoException:
                    batch[video_id].append((self.__iteration_id__, None))

                if len(batch[video_id]) == self.detect_frame_batch_size:
                    self.__logger__.info("Sending batch to video processor with id: '{}'".format(video_id))
                    self.__video_processor_list__[video_id].process_batch(batch[video_id])

                    batch[video_id] = []

            if not progress:
                break

            self.__iteration_id__ += 1

        self.__logger__.info("MainLoop done collecting frames")
