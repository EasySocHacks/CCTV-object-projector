FROM python:3.8
COPY . .
RUN pip requirements.txt
RUN python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu102/torch1.10/index.html
CMD python test.py