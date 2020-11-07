FROM python:3.9.0-alpine3.12

COPY ./requirements.txt /mnt/dynamodump/requirements.txt
COPY ./dynamodump.py /usr/local/bin/dynamodump

RUN pip install -r /mnt/dynamodump/requirements.txt
