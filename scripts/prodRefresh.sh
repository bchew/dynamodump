#!/bin/bash

python dynamodump.py -r us-east-1 -m backup -s prod-config-template-data

python dynamodump.py -r us-east-1 -m restore -s prod-config-template-data -d stage-config-template-data
