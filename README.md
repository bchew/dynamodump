dynamodump
==========

Simple backup and restore script for Amazon DynamoDB using boto to work similarly to mysqldump.

Suitable for DynamoDB usages of smaller data volume which do not warrant the usage of AWS Data Pipeline for backup/restores.

dynamodump now supports local DynamoDB instances as well (tested with dynalite).

Usage
-----
```
usage: dynamodump.py [-h] [-m MODE] [-r REGION] [-t TABLE] [--host HOST]
                     [--port PORT] [--accessKey ACCESSKEY]
                     [--secretKey SECRETKEY] [--log LOG]

Simple DynamoDB backup/restore.

required arguments:
  -m MODE, --mode MODE  'backup' or 'restore'
  -r REGION, --region REGION
                        AWS region to use, e.g. 'us-west-1'. Use 'local' for
                        local DynamoDB testing.
  -s SRCTABLE, --srcTable SRCTABLE
                        source DynamoDB table name to backup or restore from

optional arguments:
  -h, --help            show this help message and exit
  -d DESTTABLE, --destTable DESTTABLE
                        destination DynamoDB table name to backup or restore
                        to [optional, defaults to source]
  --host HOST           Host of local DynamoDB [required only for local]
  --port PORT           Port of local DynamoDB [required only for local]
  --accessKey ACCESSKEY
                        Access key of local DynamoDB [required only for local]
  --secretKey SECRETKEY
                        Secret key of local DynamoDB [required only for local]
  --log LOG             Logging level - DEBUG|INFO|WARNING|ERROR|CRITICAL
                        [optional]
```

AWS example
-----------
```
python dynamodump.py -m backup -r us-west-1 -s testTable

python dynamodump.py -m restore -r us-west-1 -s testTable
```
The above assumes your AWS access key and secret key is present in ~/.boto

Local example
-------------
```
python dynamodump.py -m backup -r local -s test-table --host localhost --port 4567 --accessKey a --secretKey a

python dynamodump.py -m restore -r local -s test-table --host localhost --port 4567 --accessKey a --secretKey a
```
The above assumes your local DynamoDB is running on localhost:4567 and is accessible via 'a' as access/secret keys.

To Do
-----
- Support handling of multiple tables
- Improve backup/restore performance
