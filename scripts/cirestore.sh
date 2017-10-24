#!/bin/bash

python dynamodump.py -a zip -b cti-dev-dynamodb-dump -m restore -r local -s stage* -d ci* --host dynamodb --port 8000

echo "### Removing temp folder ###"
rm -rf /tmp

while true
do
    sleep 100000
done
