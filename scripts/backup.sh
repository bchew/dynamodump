#!/bin/bash

python dynamodump.py -r us-east-1 -m backup -a zip -b cti-dev-dynamodb-dump -s stage-[cn][!a]*
