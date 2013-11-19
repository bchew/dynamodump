dynamodump
==========

Simple backup and restore script for Amazon DynamoDB using boto.

Suitable for DynamoDB usages of smaller data volume which do not warrant the usage of AWS Data Pipeline for backup/restores.

dynamodump now supports local DynamoDB instances as well (e.g. DynamoDB local, dynalite).

Usage
-----
```
usage: dynamodump.py [-h] [-m MODE] [-r REGION] [-t TABLE] [--host HOST]
                     [--port PORT] [--accessKey ACCESSKEY]
                     [--secretKey SECRETKEY]

Simple DynamoDB backup/restore.

optional arguments:
  -h, --help            show this help message and exit
  -m MODE, --mode MODE  'backup' or 'restore'
  -r REGION, --region REGION
                        AWS region to use, e.g. 'us-west-1'. Use 'local' for
                        local DynamoDB testing.
  -t TABLE, --table TABLE
                        DynamoDB table name to backup or restore to
  --host HOST           Host of local DynamoDB [required only for local]
  --port PORT           Port of local DynamoDB [required only for local]
  --accessKey ACCESSKEY
                        Access key of local DynamoDB [required only for local]
  --secretKey SECRETKEY
                        Secret key of local DynamoDB [required only for local]
```

AWS example
-----------
```
python dynamodump.py -m backup -r us-west-1 -t testTable

python dynamodump.py -m restore -r us-west-1 -t testTable
```
The above assumes your AWS access key and secret key is present in ~/.boto

Local example
-------------
```
python dynamodump.py -m backup -r local -t test-table --host localhost --port 4567 --accessKey a --secretKey a

python dynamodump.py -m restore -r local -t test-table --host localhost --port 4567 --accessKey a --secretKey a
```
The above assumes your DynamoDB local is running on localhost:4567 and is accessible via 'a' as access/secret keys.

To Do
-----
- Support handling of multiple tables
- Improve backup/restore performance
