dynamodump
==========

Simple backup and restore script for Amazon DynamoDB using boto to work similarly to mysqldump.

Suitable for DynamoDB usages of smaller data volume which do not warrant the usage of AWS Data Pipeline for backup/restores/empty.

dynamodump supports local DynamoDB instances as well (tested with [dynalite](https://github.com/mhart/dynalite)).

Usage
-----
```
usage: dynamodump.py [-h] [-m MODE] [-r REGION] [-s SRCTABLE] [-d DESTTABLE]
                     [--prefixSeparator PREFIXSEPARATOR] [--noSeparator]
                     [--readCapacity READCAPACITY]
                     [--writeCapacity WRITECAPACITY] [--host HOST]
                     [--port PORT] [--accessKey ACCESSKEY]
                     [--secretKey SECRETKEY] [--log LOG] [--dataOnly]

Simple DynamoDB backup/restore.

optional arguments:
  -h, --help            show this help message and exit
  -m MODE, --mode MODE  'backup' or 'restore' or 'empty'
  -r REGION, --region REGION
                        AWS region to use, e.g. 'us-west-1'. Use 'local' for
                        local DynamoDB testing.
  -s SRCTABLE, --srcTable SRCTABLE
                        Source DynamoDB table name to backup or restore from,
                        use 'tablename*' for wildcard prefix selection or '*'
                        for all tables.
  -d DESTTABLE, --destTable DESTTABLE
                        Destination DynamoDB table name to backup or restore
                        to, use 'tablename*' for wildcard prefix selection
                        (defaults to use '-' separator) [optional, defaults to
                        source]
  --prefixSeparator PREFIXSEPARATOR
                        Specify a different prefix separator, e.g. '.'
                        [optional]
  --noSeparator         Overrides the use of a prefix separator for backup
                        wildcard searches, [optional]
  --readCapacity READCAPACITY
                        Change the temp read capacity of the DynamoDB table to
                        backup from [optional]
  --writeCapacity WRITECAPACITY
                        Change the temp write capacity of the DynamoDB table
                        to restore to [defaults to 25, optional]
  --host HOST           Host of local DynamoDB [required only for local]
  --port PORT           Port of local DynamoDB [required only for local]
  --accessKey ACCESSKEY
                        Access key of local DynamoDB [required only for local]
  --secretKey SECRETKEY
                        Secret key of local DynamoDB [required only for local]
  --log LOG             Logging level - DEBUG|INFO|WARNING|ERROR|CRITICAL
                        [optional]
  --dataOnly            Restore data only. Do not delete/recreate schema
                        [optional for restore]
  --skipThroughputUpdate
                        Skip updating throughput values across tables
                        [optional]

Backup files are stored in a 'dump' subdirectory, and are restored from there as well by default.
```

AWS example
-----------
The following examples assume your AWS access key and secret key is present in ~/.boto

Single table backup/restore:
```
python dynamodump.py -m backup -r us-west-1 -s testTable

python dynamodump.py -m restore -r us-west-1 -s testTable
```
Multiple table backup/restore (assumes prefix of 'production-' of table names, use --prefixSeparator to specify a
different separator):
```
python dynamodump.py -m backup -r us-west-1 -s production*

python dynamodump.py -m restore -r us-west-1 -s production*
```
The above, but between different environments (e.g. production-* tables to development-* tables):
```
python dynamodump.py -m backup -r us-west-1 -s production*

python dynamodump.py -m restore -r us-west-1 -s production* -d development*
```
Backup all tables and restore only data (will not delete and recreate schema):
```
python dynamodump.py -m backup -r us-west-1 -s "*"

python dynamodump.py -m restore -r us-west-1 -s "*" --dataOnly
```

Local example
-------------
The following assume your local DynamoDB is running on localhost:4567 and is accessible via 'a' as access/secret keys.
```
python dynamodump.py -m backup -r local -s testTable --host localhost --port 4567 --accessKey a --secretKey a

python dynamodump.py -m restore -r local -s testTable --host localhost --port 4567 --accessKey a --secretKey a
```
Multiple table backup/restore as stated in the AWS examples are also available for local.
