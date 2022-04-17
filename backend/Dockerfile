FROM ubuntu:20.04

ARG DEVICE
ARG CUDA_VERSION=""

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ADD . .

RUN apt update
RUN apt install -y wget
RUN apt install -y make
RUN apt install -y build-essential
RUN apt install -y python3-opencv

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda

RUN conda create -y --name CCTV python=3.8
RUN activate CCTV
RUN conda install -y -c anaconda cmake
RUN conda install -y -c conda-forge ffmpeg

RUN if [ $DEVICE = "cuda" ]; \
    then \
      CUDA_VERSION_MODIFIED=$(echo ${CUDA_VERSION} | sed 's/\.//'); \
      pip install torch==1.10.0+cu$CUDA_VERSION_MODIFIED torchvision==0.11.0+cu$CUDA_VERSION_MODIFIED torchaudio==0.10.0 -f https://download.pytorch.org/whl/torch_stable.html; \
    elif [ $DEVICE = "cpu" ]; \
      then \
      pip install torch==1.10.0+cpu torchvision==0.11.0+cpu torchaudio==0.10.0 -f https://download.pytorch.org/whl/torch_stable.html; \
    else \
      echo ".env variable 'DEVICE' must be either 'cuda' or 'cpu'"; \
      exit 1; \
    fi;
RUN pip install -r requirements.txt
RUN if [ $DEVICE = "cuda" ]; \
    then \
      CUDA_VERSION_MODIFIED=$(echo ${CUDA_VERSION} | sed 's/\.//'); \
      pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu$CUDA_VERSION_MODIFIED/torch1.10/index.html; \
    elif [ $DEVICE = "cpu" ];  \
    then \
      pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/torch1.10/index.html; \
    else \
      echo ".env variable 'DEVICE' must be either 'cuda' or 'cpu'"; \
      exit 1; \
    fi;
RUN pip install -r https://raw.githubusercontent.com/ultralytics/yolov5/master/requirements.txt
ENTRYPOINT ["python", "main.py"]