#!/bin/bash

python dynamodump.py -r us-east-1 -m backup -a zip -s stage* --schemaOnly

python dynamodump.py -a zip -m restore -r local -s stage* -d dev* --host $(/sbin/ip route|awk '/default/ { print $3 }') --port 8000
