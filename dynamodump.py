import boto.dynamodb2.layer1, json, sys, time, shutil, os, argparse, logging
from boto.dynamodb2.layer1 import DynamoDBConnection

JSON_INDENT = 2
AWS_SLEEP_INTERVAL = 10 #seconds
LOCAL_SLEEP_INTERVAL = 1 #seconds
MAX_BATCH_WRITE = 25 #DynamoDB limit
SCHEMA_FILE = "schema.json"
DATA_DIR = "data"
MAX_RETRY = 3
LOCAL_REGION = "local"
LOG_LEVEL = "INFO"

def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else: raise

def batch_write(conn, table_name, put_requests):
  request_items = {table_name: put_requests}
  i = 1
  while True:
    response = conn.batch_write_item(request_items)
    unprocessed_items = response["UnprocessedItems"]

    if len(unprocessed_items) == 0:
      break

    if len(unprocessed_items) > 0 and i <= MAX_RETRY:
      logging.info(len(unprocessed_items) + " unprocessed items, retrying.. [" + str(i) + "]")
      request_items = unprocessed_items
      i += 1
    else:
      logging.info("Max retries reached, failed to processed batch write: " + unprocessed_items)
      logging.info("Ignoring and continuing..")
      break

def do_backup(table_name):
  # trash data, re-create subdir
  if os.path.exists(table_name):
    shutil.rmtree(table_name)
  mkdir_p(table_name)

  # get table schema
  logging.info("Dumping table schema for " + table_name)
  f = open(table_name + "/" + SCHEMA_FILE, "w+")
  f.write(json.dumps(conn.describe_table(table_name), indent=JSON_INDENT))
  f.close()

  # get table data
  logging.info("Dumping table items for " + table_name)
  mkdir_p(table_name + "/" + DATA_DIR)

  i = 1
  last_evaluated_key = None

  while True:
    scanned_table = conn.scan(table_name, exclusive_start_key=last_evaluated_key)

    f = open(table_name + "/" + DATA_DIR + "/" + str(i).zfill(4) + ".json", "w+")
    f.write(json.dumps(scanned_table, indent=JSON_INDENT))
    f.close()

    i += 1

    try:
      last_evaluated_key = scanned_table["LastEvaluatedKey"]
    except KeyError, e:
      break

def do_restore(sleep_interval, source_table, destination_table):
  if destination_table == None:
    destination_table = source_table

  # delete table if exists
  table_exist = True
  try:
    conn.delete_table(destination_table)
  except boto.exception.JSONResponseError, e:
    if e.body["__type"] == "com.amazonaws.dynamodb.v20120810#ResourceNotFoundException":
      table_exist = False
      logging.info("Table does not exist in destination, skip waiting..")
      pass
    else:
      logging.exception(e)
      sys.exit(1)

  # if table exists, wait till deleted
  if table_exist:
    try:
      while True:
        logging.info("Waiting for " + destination_table + " table to be deleted.. [" + conn.describe_table(destination_table)["Table"]["TableStatus"] +"]")
        time.sleep(sleep_interval)
    except boto.exception.JSONResponseError, e:
      if e.body["__type"] == "com.amazonaws.dynamodb.v20120810#ResourceNotFoundException":
        logging.info(destination_table + " table deleted.")
        pass
      else:
        logging.exception(e)
        sys.exit(1)

  # create table using schema
  table_data = json.load(open(source_table + "/" + SCHEMA_FILE))
  table = table_data["Table"]
  table_attribute_definitions = table["AttributeDefinitions"]
  table_table_name = destination_table
  table_key_schema = table["KeySchema"]
  table_provisioned_throughput = table["ProvisionedThroughput"]
  table_local_secondary_indexes = table.get("LocalSecondaryIndexes")

  conn.create_table(table_attribute_definitions, table_table_name, table_key_schema, table_provisioned_throughput, table_local_secondary_indexes)

  # wait for table creation completion
  while True:
    if conn.describe_table(destination_table)["Table"]["TableStatus"] != "ACTIVE":
      logging.info("Waiting for " + destination_table + " table to be created.. [" + conn.describe_table(destination_table)["Table"]["TableStatus"] +"]")
      time.sleep(sleep_interval)
    else:
      logging.info(destination_table + " created.")
      break

  # read data files
  logging.info("Restoring data for " + destination_table + " table..")
  data_file_list = os.listdir(source_table + "/" + DATA_DIR + "/")
  data_file_list.sort()

  items = []
  for data_file in data_file_list:
    item_data = json.load(open(source_table + "/" + DATA_DIR + "/" + data_file))
    items.extend(item_data["Items"])

  # batch write data
  put_requests = []
  while len(items) > 0:
    put_requests.append({"PutRequest": {"Item": items.pop(0)}})

    # flush every MAX_BATCH_WRITE
    if len(put_requests) == MAX_BATCH_WRITE:
      batch_write(conn, destination_table, put_requests)
      del put_requests[:]

  # flush remainder
  batch_write(conn, destination_table, put_requests)

# parse args
parser = argparse.ArgumentParser(description="Simple DynamoDB backup/restore.")
parser.add_argument("-m", "--mode", help="'backup' or 'restore'")
parser.add_argument("-r", "--region", help="AWS region to use, e.g. 'us-west-1'. Use '" + LOCAL_REGION + "' for local DynamoDB testing.")
parser.add_argument("-s", "--srcTable", help="source DynamoDB table name to backup or restore from")
parser.add_argument("-d", "--destTable", help="destination DynamoDB table name to backup or restore to [optional, defaults to source]")
parser.add_argument("--host", help="Host of local DynamoDB [required only for local]")
parser.add_argument("--port", help="Port of local DynamoDB [required only for local]")
parser.add_argument("--accessKey", help="Access key of local DynamoDB [required only for local]")
parser.add_argument("--secretKey", help="Secret key of local DynamoDB [required only for local]")
parser.add_argument("--log", help="Logging level - DEBUG|INFO|WARNING|ERROR|CRITICAL [optional]")
args = parser.parse_args()

# set log level
log_level = LOG_LEVEL
if args.log != None:
  log_level = args.log.upper()
logging.basicConfig(level=getattr(logging, log_level))

# instantiate connection
if args.region == LOCAL_REGION:
  conn = DynamoDBConnection(aws_access_key_id=args.accessKey, aws_secret_access_key=args.secretKey, host=args.host, port=int(args.port), is_secure=False)
  sleep_interval = LOCAL_SLEEP_INTERVAL
else:
  conn = boto.dynamodb2.connect_to_region(args.region)
  sleep_interval = AWS_SLEEP_INTERVAL

# do backup/restore
if args.mode == "backup":
  logging.info("Starting backup for " + args.srcTable + "..")
  do_backup(args.srcTable)
  logging.info("Backup for " + args.srcTable + " table completed.")
elif args.mode == "restore":
  restore_str = args.srcTable
  if args.destTable != None:
    restore_str = restore_str + " to " + args.destTable
  logging.info("Starting restore for " + restore_str + "..")
  do_restore(sleep_interval, args.srcTable, args.destTable)
  logging.info("Restore for " + restore_str + " table completed.")
