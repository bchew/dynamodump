FROM python:3.10.8-alpine3.16

COPY ./requirements.txt /mnt/dynamodump/requirements.txt
COPY ./dynamodump/dynamodump.py /usr/local/bin/dynamodump

RUN pip install -r /mnt/dynamodump/requirements.txt

ENTRYPOINT ["dynamodump"]
CMD ["-h"]
