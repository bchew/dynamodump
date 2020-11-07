
FROM python:2.7.14-alpine3.7

COPY ./requirements.txt /mnt/dynamodump/requirements.txt
COPY ./dynamodump.py /usr/local/bin/dynamodump

RUN pip install -r /mnt/dynamodump/requirements.txt
