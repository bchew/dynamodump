FROM python:2.7

ADD ./.boto /root 
ADD ./scripts /scripts

ADD ./src/ /dynamodump

WORKDIR /dynamodump

RUN pip install -r requirements.txt
