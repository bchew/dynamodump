import boto.dynamodb2.layer1, json, sys, time, shutil, os, argparse
from boto.dynamodb2.layer1 import DynamoDBConnection

JSON_INDENT = 2
AWS_SLEEP_INTERVAL = 10 #seconds
LOCAL_SLEEP_INTERVAL = 1 #seconds
MAX_BATCH_WRITE = 25 #DynamoDB limit
SCHEMA_FILE = "schema.json"
DATA_DIR = "data"
MAX_RETRY = 3
LOCAL_REGION = "local"

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
      print len(unprocessed_items) + " unprocessed items, retrying.. [" + str(i) + "]"
      request_items = unprocessed_items
      i += 1
    else:
      print "Max retries reached, failed to processed batch write: " + unprocessed_items
      print "Ignoring and continuing.."
      break

def do_backup(table_name):
  # trash data, re-create subdir
  shutil.rmtree(table_name)
  mkdir_p(table_name)

  # get table schema
  print "Dumping table schema for " + table_name
  f = open(table_name + "/" + SCHEMA_FILE, "w+")
  f.write(json.dumps(conn.describe_table(table_name), indent=JSON_INDENT))
  f.close()

  # get table data
  print "Dumping table items for " + table_name
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

def do_restore(table_name, sleep_interval):
  # delete table if exists
  try:
    conn.delete_table(table_name)
  except boto.exception.JSONResponseError, e:
    if e.body["__type"] == "com.amazonaws.dynamodb.v20120810#ResourceNotFoundException":
      pass

  # if table exists, wait till deleted
  try:
    while True:
      print "Waiting for " + table_name + " table to be deleted.. [" + conn.describe_table(table_name)["Table"]["TableStatus"] +"]"
      time.sleep(sleep_interval)
  except boto.exception.JSONResponseError, e:
    if e.body["__type"] == "com.amazonaws.dynamodb.v20120810#ResourceNotFoundException":
      print table_name + " deleted."
      pass

  # create table using schema
  table_data = json.load(open(table_name + "/" + SCHEMA_FILE))
  table = table_data["Table"]
  table_attribute_definitions = table["AttributeDefinitions"]
  table_table_name = table["TableName"]
  table_key_schema = table["KeySchema"]
  table_provisioned_throughput = table["ProvisionedThroughput"]
  table_local_secondary_indexes = table.get("LocalSecondaryIndexes")

  conn.create_table(table_attribute_definitions, table_table_name, table_key_schema, table_provisioned_throughput, table_local_secondary_indexes)

  # wait for table creation completion
  while True:
    if conn.describe_table(table_name)["Table"]["TableStatus"] != "ACTIVE":
      print "Waiting for " + table_name + " table to be created.. [" + conn.describe_table(table_name)["Table"]["TableStatus"] +"]"
      time.sleep(sleep_interval)
    else:
      print table_name + " created."
      break

  # read data files
  print "Restoring data for " + table_name + " table.."
  data_file_list = os.listdir(table_name + "/" + DATA_DIR + "/")
  data_file_list.sort()

  items = []
  for data_file in data_file_list:
    item_data = json.load(open(table_name + "/" + DATA_DIR + "/" + data_file))
    items.extend(item_data["Items"])

  # batch write data
  put_requests = []
  while len(items) > 0:
    put_requests.append({"PutRequest": {"Item": items.pop(0)}})

    # flush every MAX_BATCH_WRITE
    if len(put_requests) == MAX_BATCH_WRITE:
      batch_write(conn, table_name, put_requests)
      del put_requests[:]

  # flush remainder
  batch_write(conn, table_name, put_requests)

# parse args
parser = argparse.ArgumentParser(description="Simple DynamoDB backup/restore.")
parser.add_argument("-m", "--mode", help="'backup' or 'restore'")
parser.add_argument("-r", "--region", help="AWS region to use, e.g. 'us-west-1'. Use '" + LOCAL_REGION + "' for local DynamoDB testing.")
parser.add_argument("-t", "--table", help="DynamoDB table name to backup or restore to")
parser.add_argument("--host", help="Host of local DynamoDB [required only for local]")
parser.add_argument("--port", help="Port of local DynamoDB [required only for local]")
parser.add_argument("--accessKey", help="Access key of local DynamoDB [required only for local]")
parser.add_argument("--secretKey", help="Secret key of local DynamoDB [required only for local]")
args = parser.parse_args()

# instantiate connection
if args.region == LOCAL_REGION:
  conn = DynamoDBConnection(aws_access_key_id=args.accessKey, aws_secret_access_key=args.secretKey, host=args.host, port=int(args.port), is_secure=False)
  sleep_interval = LOCAL_SLEEP_INTERVAL
else:
  conn = boto.dynamodb2.connect_to_region(args.region)
  sleep_interval = AWS_SLEEP_INTERVAL

# do backup/restore
if args.mode == "backup":
  print "Starting backup for " + args.table + ".."
  do_backup(args.table)
  print "Backup for " + args.table + " table completed."
elif args.mode == "restore":
  print "Starting restore for " + args.table + ".."
  do_restore(args.table, sleep_interval)
  print "Restore for " + args.table + " table completed."
