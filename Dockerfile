FROM python:3.9.6-alpine3.14

COPY ./requirements.txt /mnt/dynamodump/requirements.txt
COPY ./dynamodump/dynamodump.py /usr/local/bin/dynamodump

RUN pip install -r /mnt/dynamodump/requirements.txt
