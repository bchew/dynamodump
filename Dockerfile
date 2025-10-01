FROM python:3.13.7-alpine

COPY ./requirements.txt /mnt/dynamodump/requirements.txt
COPY ./dynamodump/dynamodump.py /usr/local/bin/dynamodump

RUN pip install -r /mnt/dynamodump/requirements.txt

ENTRYPOINT ["dynamodump"]
CMD ["-h"]
