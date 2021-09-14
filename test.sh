#!/bin/bash -e
# Test script which assumes DynamoDB Local is ready and available via `docker-compose up`

# Test basic restore and backup
mkdir -p dump && cp -a tests/testTable dump
python dynamodump/dynamodump.py -m restore --noConfirm -r local -s testTable -d testRestoredTable \
  --host localhost --port 8000 --accessKey a --secretKey a
python dynamodump/dynamodump.py -m backup -r local -s testRestoredTable --host localhost --port 8000 \
  --accessKey a --secretKey a
python tests/test.py

# Test wildcard restore and backup with PAY_BY_REQUEST BillingMode
python dynamodump/dynamodump.py -m restore --noConfirm -r local -s "*" --host localhost --port 8000 \
  --accessKey a --secretKey a --billingMode "PAY_BY_REQUEST"
rm -rf dump/test*
python dynamodump/dynamodump.py -m backup -r local -s "*" --host localhost --port 8000 --accessKey a \
  --secretKey a
python tests/test.py

# Test wildcard restore and backup
python dynamodump/dynamodump.py -m restore --noConfirm -r local -s "*" --host localhost --port 8000 \
  --accessKey a --secretKey a
rm -rf dump/test*
python dynamodump/dynamodump.py -m backup -r local -s "*" --host localhost --port 8000 --accessKey a \
  --secretKey a
python tests/test.py

# Test prefixed wildcard restore and backup
python dynamodump/dynamodump.py -m restore --noConfirm -r local -s "test*" --host localhost --port 8000 \
  --accessKey a --secretKey a --prefixSeparator ""
rm -rf dump/test*
python dynamodump/dynamodump.py -m backup -r local -s "test*" --host localhost --port 8000 --accessKey a \
  --secretKey a --prefixSeparator ""
python tests/test.py

# Clean up
rm -rf dump/test*
