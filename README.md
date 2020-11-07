dynamodump
==========

![Build Status](https://github.com/bchew/dynamodump/workflows/Python%20package/badge.svg) [![DockerBuildstatus](https://img.shields.io/docker/build/bchew/dynamodump.svg)](https://hub.docker.com/r/bchew/dynamodump/)

Simple backup and restore script for Amazon DynamoDB using boto to work similarly to mysqldump.

Suitable for DynamoDB usages of smaller data volume which do not warrant the usage of AWS Data Pipeline for backup/restores/empty.

dynamodump supports local DynamoDB instances as well (tested with [DynamoDB Local](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html)).

Usage
-----
```
usage: dynamodump.py [-h] [-a {zip,tar}] [-b BUCKET]
                     [-m {backup,restore,empty}] [-r REGION] [--host HOST]
                     [--port PORT] [--accessKey ACCESSKEY]
                     [--secretKey SECRETKEY] [-p PROFILE] [-s SRCTABLE]
                     [-d DESTTABLE] [--prefixSeparator PREFIXSEPARATOR]
                     [--noSeparator] [--readCapacity READCAPACITY] [-t TAG]
                     [--writeCapacity WRITECAPACITY] [--schemaOnly]
                     [--dataOnly] [--skipThroughputUpdate]
                     [--dumpPath DUMPPATH] [--log LOG]

Simple DynamoDB backup/restore/empty.

optional arguments:
  -h, --help            show this help message and exit
  -a {zip,tar}, --archive {zip,tar}
                        Type of compressed archive to create.If unset, don't
                        create archive
  -b BUCKET, --bucket BUCKET
                        S3 bucket in which to store or retrieve backups.[must
                        already exist]
  -m {backup,restore,empty}, --mode {backup,restore,empty}
                        Operation to perform
  -r REGION, --region REGION
                        AWS region to use, e.g. 'us-west-1'. Can use
                        AWS_DEFAULT_REGION for local testing. Use 'local' for
                        local DynamoDB testing
  --host HOST           Host of local DynamoDB [required only for local]
  --port PORT           Port of local DynamoDB [required only for local]
  --accessKey ACCESSKEY
                        Access key of local DynamoDB [required only for local]
  --secretKey SECRETKEY
                        Secret key of local DynamoDB [required only for local]
  -p PROFILE, --profile PROFILE
                        AWS credentials file profile to use. Allows you to use
                        a profile instead accessKey, secretKey authentication
  -s SRCTABLE, --srcTable SRCTABLE
                        Source DynamoDB table name to backup or restore from,
                        use 'tablename*' for wildcard prefix selection or '*'
                        for all tables. Mutually exclusive with --tag
  -d DESTTABLE, --destTable DESTTABLE
                        Destination DynamoDB table name to backup or restore
                        to, use 'tablename*' for wildcard prefix selection
                        (defaults to use '-' separator) [optional, defaults to
                        source]
  --prefixSeparator PREFIXSEPARATOR
                        Specify a different prefix separator, e.g. '.'
                        [optional]
  --noSeparator         Overrides the use of a prefix separator for backup
                        wildcard searches [optional]
  --readCapacity READCAPACITY
                        Change the temp read capacity of the DynamoDB table to
                        backup from [optional]
  -t TAG, --tag TAG     Tag to use for identifying tables to back up. Mutually
                        exclusive with srcTable. Provided as KEY=VALUE
  --writeCapacity WRITECAPACITY
                        Change the temp write capacity of the DynamoDB table
                        to restore to [defaults to 25, optional]
  --schemaOnly          Backup or restore the schema only. Do not
                        backup/restore data. Can be used with both backup and
                        restore modes. Cannot be used with the --dataOnly
                        [optional]
  --dataOnly            Restore data only. Do not delete/recreate schema
                        [optional for restore]
  --skipThroughputUpdate
                        Skip updating throughput values across tables
                        [optional]
  --dumpPath DUMPPATH   Directory to place and search for DynamoDB table
                        backups (defaults to use 'dump') [optional]
  --log LOG             Logging level - DEBUG|INFO|WARNING|ERROR|CRITICAL
                        [optional]
```

Backup files are stored in a 'dump' subdirectory, and are restored from there as well by default.

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
Dump all table schemas and create the schemas (e.g. creating blank tables in a different AWS account):
```
python dynamodump.py -m backup -r us-west-1 -p source_credentials -s "*" --schemaOnly

python dynamodump.py -m restore -r us-west-1 -p destination_credentials -s "*" --schemaOnly
```

Backup all tables based on AWS tag `key=value`
```
python dynamodump.py -p profile -r us-east-1 -m backup -t KEY=VALUE
```

Backup all tables based on AWS tag, compress and store in specified S3 bucket.
```
python dynamodump.py -p profile -r us-east-1 -m backup -a tar -b some_s3_bucket -t TAG_KEY=TAG_VALUE

python dynamodump.py -p profile -r us-east-1 -m backup -a zip -b some_s3_bucket -t TAG_KEY=TAG_VALUE
```

Restore from S3 bucket to specified destination table
```
## source_table identifies archive file in S3 bucket from which backup data is restored
python2 dynamodump.py -a tar -b some_s3_bucket -m restore -r us-east-1 -p profile -d destination_table -s source_table
```

Local example
-------------
The following assume your local DynamoDB is running on localhost:8000 and is accessible via 'a' as access/secret keys.
```
python dynamodump.py -m backup -r local -s testTable --host localhost --port 8000 --accessKey a --secretKey a

python dynamodump.py -m restore -r local -s testTable --host localhost --port 8000 --accessKey a --secretKey a
```
Multiple table backup/restore as stated in the AWS examples are also available for local.
