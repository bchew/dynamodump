#!/bin/bash

python dynamodump.py -a zip -b cti-dev-dynamodb-dump -m restore -r local -s stage* -d dev* --host $(/sbin/ip route|awk '/default/ { print $3 }') --port 8000
