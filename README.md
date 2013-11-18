dynamodump
==========

Simple backup and restore script for Amazon DynamoDB using boto. Suitable for DynamoDB usages of smaller data volume which do not warrant the usage of AWS Data Pipeline for backup/restores.

Example
-------
```
usage: dynamodump.py [-h] [-m MODE] [-r REGION] [-t TABLE]

Simple DynamoDB backup/restore

optional arguments:
  -h, --help            show this help message and exit
  -m MODE, --mode MODE  'backup' or 'restore'
  -r REGION, --region REGION
                        AWS region to use, e.g. 'us-west-1'
  -t TABLE, --table TABLE
                        DynamoDB table name to backup or restore to
```

The script assumes your AWS access key and secret key is present in ~/.boto


To Do
-----
- Support backup/restore to local DynamoDB installs
- Support handling of multiple tables
- Improve backup/restore performance
