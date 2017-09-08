#!/bin/bash

python dynamodump.py -a zip -b cti-dev-dynamodb-dump -m restore -r local -s stage* -d ci* --host dynamodb --port 8000

rm -rf /tmp

bash
