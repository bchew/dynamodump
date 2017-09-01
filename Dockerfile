FROM python:2.7

ADD ./.boto /root 
ADD ./scripts /scripts

ADD ./dynamodump/ /dynamodump

WORKDIR /dynamodump

RUN pip install -r requirements.txt
