# dynamodump

![Build Status](https://github.com/bchew/dynamodump/actions/workflows/build.yml/badge.svg)
![CodeQL Status](https://github.com/bchew/dynamodump/actions/workflows/codeql-analysis.yml/badge.svg)
[![Docker Status](https://github.com/bchew/dynamodump/actions/workflows/docker.yml/badge.svg)](https://hub.docker.com/r/bchew/dynamodump)
![Linting Status](https://github.com/bchew/dynamodump/actions/workflows/linting.yml/badge.svg)
![Test Status](https://github.com/bchew/dynamodump/actions/workflows/test.yml/badge.svg)
[![PyPI version](https://img.shields.io/pypi/v/dynamodump)](https://pypi.org/project/dynamodump)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/dynamodump.svg)](https://pypi.org/project/dynamodump)
![Code Style](https://img.shields.io/badge/code%20style-black-black)

Simple backup and restore script for Amazon DynamoDB using AWS SDK for Python (boto3) to work similarly to mysqldump.

Suitable for DynamoDB usages of smaller data volume which do not warrant the usage of AWS Data Pipeline for backup/restores/empty.

dynamodump supports local DynamoDB instances as well (tested with [DynamoDB Local](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html)).

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Script (unattended) usage](#script-unattended-usage)
- [Docker CLI usage](#docker-cli-usage)
- [AWS example](#aws-example)
- [Local example](#local-example)
- [Development](#development)

## Installation

```
pip install dynamodump
```

## Usage

```
usage: dynamodump.py [-h] [-a {zip,tar}] [-b BUCKET] [-m {backup,restore,empty}] [-r REGION] [--host HOST] [--port PORT] [--accessKey ACCESSKEY] [--secretKey SECRETKEY] [-p PROFILE] [-s SRCTABLE] [-d DESTTABLE]
                     [--prefixSeparator PREFIXSEPARATOR] [--noSeparator] [--readCapacity READCAPACITY] [-t TAG] [--writeCapacity WRITECAPACITY] [--schemaOnly] [--dataOnly] [--noConfirm] [--skipThroughputUpdate]
                     [--dumpPath DUMPPATH] [--billingMode {PROVISIONED,PAY_PER_REQUEST}] [--log LOG] [--limit LIMIT] [-f FILTEROPTION]

Simple DynamoDB backup/restore/empty.

options:
  -h, --help            show this help message and exit
  -a {zip,tar}, --archive {zip,tar}
                        Type of compressed archive to create. If unset, don't create archive
  -b BUCKET, --bucket BUCKET
                        S3 bucket in which to store or retrieve backups. [must already exist]
  -m {backup,restore,empty}, --mode {backup,restore,empty}
                        Operation to perform
  -r REGION, --region REGION
                        AWS region to use, e.g. 'us-west-1'. Can use any region for local testing
  --host HOST           Host of local DynamoDB. This parameter initialises dynamodump for local DynamoDB testing [required only for local]
  --port PORT           Port of local DynamoDB [required only for local]
  --accessKey ACCESSKEY
                        Access key of local DynamoDB [required only for local]
  --secretKey SECRETKEY
                        Secret key of local DynamoDB [required only for local]
  -p PROFILE, --profile PROFILE
                        AWS credentials file profile to use. Allows you to use a profile instead accessKey, secretKey authentication
  -s SRCTABLE, --srcTable SRCTABLE
                        Source DynamoDB table name to backup or restore from, use 'tablename*' for wildcard prefix selection or '*' for all tables. Mutually exclusive with --tag
  -d DESTTABLE, --destTable DESTTABLE
                        Destination DynamoDB table name to backup or restore to, use 'tablename*' for wildcard prefix selection (defaults to use '-' separator) [optional, defaults to source]
  --prefixSeparator PREFIXSEPARATOR
                        Specify a different prefix separator, e.g. '.' [optional]
  --noSeparator         Overrides the use of a prefix separator for backup wildcard searches [optional]
  --readCapacity READCAPACITY
                        Change the temp read capacity of the DynamoDB table to backup from [optional]
  -t TAG, --tag TAG     Tag to use for identifying tables to back up. Mutually exclusive with srcTable. Provided as KEY=VALUE
  --writeCapacity WRITECAPACITY
                        Change the temp write capacity of the DynamoDB table to restore to [defaults to 25, optional]
  --schemaOnly          Backup or restore the schema only. Do not backup/restore data. Can be used with both backup and restore modes. Cannot be used with the --dataOnly [optional]
  --dataOnly            Restore data only. Do not delete/recreate schema [optional for restore]
  --noConfirm           Don't ask for confirmation before deleting existing schemas.
  --skipThroughputUpdate
                        Skip updating throughput values across tables [optional]
  --dumpPath DUMPPATH   Directory to place and search for DynamoDB table backups (defaults to use 'dump') [optional]
  --billingMode {PROVISIONED,PAY_PER_REQUEST}
                        Set billing mode between PROVISIONED|PAY_PER_REQUEST (defaults to use 'PROVISIONED') [optional]
  --log LOG             Logging level - DEBUG|INFO|WARNING|ERROR|CRITICAL [optional]
  --limit LIMIT         Limit option for backup, will stop the back up process after number of backed up items reaches the limit [optional]
  -f FILTEROPTION, --filterOption FILTEROPTION
                        Filter option for backup, JSON file of which keys are ['FilterExpression', 'ExpressionAttributeNames', 'ExpressionAttributeValues']
```

Backup files are stored in a 'dump' subdirectory, and are restored from there as well by default.

## Script (unattended) usage

As of v1.2.0, note that `--noConfirm` is required to perform data restores involving deletions without any confirmation.

## Docker CLI usage

```
docker run --rm -it bchew/dynamodump -h
```

dynamodump container images are also published to Amazon ECR Public and GitHub Packages:

```
public.ecr.aws/bchew/dynamodump
ghcr.io/bchew/dynamodump
```

Links to the registries specified:
- [Docker Hub](https://hub.docker.com/r/bchew/dynamodump)
- [Amazon ECR Public Gallery](https://gallery.ecr.aws/bchew/dynamodump)
- [GitHub Packages](https://github.com/bchew/dynamodump/pkgs/container/dynamodump)

## AWS example

Single table backup/restore:

```
dynamodump -m backup -r us-west-1 -s testTable

dynamodump -m restore -r us-west-1 -s testTable
```

Multiple table backup/restore (assumes prefix of 'production-' of table names, use --prefixSeparator to specify a
different separator):

```
dynamodump -m backup -r us-west-1 -s production*

dynamodump -m restore -r us-west-1 -s production*
```

The above, but between different environments (e.g. production-_ tables to development-_ tables):

```
dynamodump -m backup -r us-west-1 -s production*

dynamodump -m restore -r us-west-1 -s production* -d development*
```

Backup all tables and restore only data (will not delete and recreate schema):

```
dynamodump -m backup -r us-west-1 -s "*"

dynamodump -m restore -r us-west-1 -s "*" --dataOnly
```

Dump all table schemas and create the schemas (e.g. creating blank tables in a different AWS account):

```
dynamodump -m backup -r us-west-1 -p source_credentials -s "*" --schemaOnly

dynamodump -m restore -r us-west-1 -p destination_credentials -s "*" --schemaOnly
```

Backup all tables based on AWS tag `key=value`

```
dynamodump -p profile -r us-east-1 -m backup -t KEY=VALUE
```

Backup all tables based on AWS tag, compress and store in specified S3 bucket.

```
dynamodump -p profile -r us-east-1 -m backup -a tar -b some_s3_bucket -t TAG_KEY=TAG_VALUE

dynamodump -p profile -r us-east-1 -m backup -a zip -b some_s3_bucket -t TAG_KEY=TAG_VALUE
```

Restore from S3 bucket to specified destination table

```
## source_table identifies archive file in S3 bucket from which backup data is restored
dynamodump -a tar -b some_s3_bucket -m restore -r us-east-1 -p profile -d destination_table -s source_table
```

## Local example

The following assumes your local DynamoDB is running on localhost:8000 and is accessible via 'a' as access/secret keys.
You must specify the host to get local behavior.

```
dynamodump -m backup -r local -s testTable --host localhost --port 8000 --accessKey a --secretKey a

dynamodump -m restore -r local -s testTable --host localhost --port 8000 --accessKey a --secretKey a
```

Multiple table backup/restore as stated in the AWS examples are also available for local.

## Development

```
python3 -m venv env
source env/bin/activate

# install dev requirements
pip3 install -r requirements-dev.txt

# one-time install of pre-commit hooks
pre-commit install
```
