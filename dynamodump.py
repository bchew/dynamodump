import boto.dynamodb2.layer1, json, sys, time, shutil, os, argparse, logging, datetime
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
DUMP_PATH = "dump"
RESTORE_WRITE_CAPACITY = 100

def get_table_name_matches(conn, table_name_wildcard):
  matching_tables = []
  table_list = conn.list_tables()["TableNames"]
  for table_name in table_list:
    if table_name.startswith(table_name_wildcard.split("*", 1)[0]):
      matching_tables.append(table_name)

  return matching_tables

def get_restore_table_matches(table_name_wildcard):
  matching_tables = []
  dir_list = os.listdir("./" + DUMP_PATH)
  for dir_name in dir_list:
    if dir_name.startswith(table_name_wildcard.split("*", 1)[0]):
      matching_tables.append(dir_name)

  return matching_tables

def change_prefix(source_table_name, source_wildcard, destination_wildcard):
  source_prefix = source_wildcard.split("*", 1)[0]
  destination_prefix = destination_wildcard.split("*", 1)[0]
  if source_table_name.split("-", 1)[0] == source_prefix:
    return destination_prefix + "-" + source_table_name.split("-", 1)[1]

def delete_table(conn, sleep_interval, table_name):
  # delete table if exists
  table_exist = True
  try:
    conn.delete_table(table_name)
  except boto.exception.JSONResponseError, e:
    if e.body["__type"] == "com.amazonaws.dynamodb.v20120810#ResourceNotFoundException":
      table_exist = False
      logging.info("Table does not exist in destination, deleting not necessary..")
      pass
    else:
      logging.exception(e)
      sys.exit(1)

  # if table exists, wait till deleted
  if table_exist:
    try:
      while True:
        logging.info("Waiting for " + table_name + " table to be deleted.. [" + conn.describe_table(table_name)["Table"]["TableStatus"] +"]")
        time.sleep(sleep_interval)
    except boto.exception.JSONResponseError, e:
      if e.body["__type"] == "com.amazonaws.dynamodb.v20120810#ResourceNotFoundException":
        logging.info(table_name + " table deleted.")
        pass
      else:
        logging.exception(e)
        sys.exit(1)

def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else: raise

def batch_write(conn, sleep_interval, table_name, put_requests):
  request_items = {table_name: put_requests}
  i = 1
  while True:
    response = conn.batch_write_item(request_items)
    unprocessed_items = response["UnprocessedItems"]

    if len(unprocessed_items) == 0:
      break

    if len(unprocessed_items) > 0 and i <= MAX_RETRY:
      logging.info(str(len(unprocessed_items)) + " unprocessed items, retrying.. [" + str(i) + "]")
      request_items = unprocessed_items
      i += 1
      time.sleep(sleep_interval)
    else:
      logging.info("Max retries reached, failed to processed batch write: " + json.dumps(unprocessed_items, indent=JSON_INDENT))
      logging.info("Ignoring and continuing..")
      break

def wait_for_active_table(conn, table_name, verb):
  while True:
    if conn.describe_table(table_name)["Table"]["TableStatus"] != "ACTIVE":
      logging.info("Waiting for " + table_name + " table to be " + verb + ".. [" + conn.describe_table(table_name)["Table"]["TableStatus"] +"]")
      time.sleep(sleep_interval)
    else:
      logging.info(table_name + " " + verb + ".")
      break

def update_provisioned_throughput(conn, table_name, read_capacity, write_capacity, wait=True):
  logging.info("Updating " + table_name + " table read capacity to: " + str(read_capacity) + ", write capacity to: " + str(write_capacity))
  conn.update_table(table_name, {"ReadCapacityUnits": int(read_capacity), "WriteCapacityUnits": int(write_capacity)})

  # wait for provisioned throughput update completion
  if wait:
    wait_for_active_table(conn, table_name, "updated")

def do_backup(conn, table_name, read_capacity):
  logging.info("Starting backup for " + table_name + "..")

  # trash data, re-create subdir
  if os.path.exists(DUMP_PATH + "/" + table_name):
    shutil.rmtree(DUMP_PATH + "/" + table_name)
  mkdir_p(DUMP_PATH + "/" + table_name)

  # get table schema
  logging.info("Dumping table schema for " + table_name)
  f = open(DUMP_PATH + "/" + table_name + "/" + SCHEMA_FILE, "w+")
  table_desc = conn.describe_table(table_name)
  f.write(json.dumps(table_desc, indent=JSON_INDENT))
  f.close()

  # override table read capacity if specified
  if (read_capacity != None):
    original_read_capacity = table_desc["Table"]["ProvisionedThroughput"]["ReadCapacityUnits"]
    original_write_capacity = table_desc["Table"]["ProvisionedThroughput"]["WriteCapacityUnits"]
    update_provisioned_throughput(conn, table_name, read_capacity, original_write_capacity)

  # get table data
  logging.info("Dumping table items for " + table_name)
  mkdir_p(DUMP_PATH + "/" + table_name + "/" + DATA_DIR)

  i = 1
  last_evaluated_key = None

  while True:
    scanned_table = conn.scan(table_name, exclusive_start_key=last_evaluated_key)

    f = open(DUMP_PATH + "/" + table_name + "/" + DATA_DIR + "/" + str(i).zfill(4) + ".json", "w+")
    f.write(json.dumps(scanned_table, indent=JSON_INDENT))
    f.close()

    i += 1

    try:
      last_evaluated_key = scanned_table["LastEvaluatedKey"]
    except KeyError, e:
      break

  # revert back to original table read capacity if specified
  if (read_capacity != None):
    update_provisioned_throughput(conn, table_name, original_read_capacity, original_write_capacity, False)

  logging.info("Backup for " + table_name + " table completed. Time taken: " + str(datetime.datetime.now().replace(microsecond=0) - start_time))

def do_restore(conn, sleep_interval, source_table, destination_table, write_capacity):
  logging.info("Starting restore for " + source_table + " to " + destination_table + "..")

  # create table using schema
  table_data = json.load(open(DUMP_PATH + "/" + source_table + "/" + SCHEMA_FILE))
  table = table_data["Table"]
  table_attribute_definitions = table["AttributeDefinitions"]
  table_table_name = destination_table
  table_key_schema = table["KeySchema"]
  original_read_capacity = table["ProvisionedThroughput"]["ReadCapacityUnits"]
  original_write_capacity = table["ProvisionedThroughput"]["WriteCapacityUnits"]
  table_local_secondary_indexes = table.get("LocalSecondaryIndexes")
  table_global_secondary_indexes = table.get("GlobalSecondaryIndexes")

  # override table write capacity if specified, else use RESTORE_WRITE_CAPACITY
  if (write_capacity == None):
    write_capacity = RESTORE_WRITE_CAPACITY

  # temp provisioned throughput for restore
  table_provisioned_throughput = {"ReadCapacityUnits": int(original_read_capacity), "WriteCapacityUnits": int(write_capacity)}

  logging.info("Creating " + destination_table + " table with temp write capacity of " + str(write_capacity))
  conn.create_table(table_attribute_definitions, table_table_name, table_key_schema, table_provisioned_throughput, table_local_secondary_indexes, table_global_secondary_indexes)

  # wait for table creation completion
  wait_for_active_table(conn, destination_table, "created")

  # read data files
  logging.info("Restoring data for " + destination_table + " table..")
  data_file_list = os.listdir(DUMP_PATH + "/" + source_table + "/" + DATA_DIR + "/")
  data_file_list.sort()

  items = []
  for data_file in data_file_list:
    item_data = json.load(open(DUMP_PATH + "/" + source_table + "/" + DATA_DIR + "/" + data_file))
    items.extend(item_data["Items"])

  # batch write data
  put_requests = []
  while len(items) > 0:
    put_requests.append({"PutRequest": {"Item": items.pop(0)}})

    # flush every MAX_BATCH_WRITE
    if len(put_requests) == MAX_BATCH_WRITE:
      logging.debug("Writing next " + str(MAX_BATCH_WRITE) + " items to " + destination_table + "..")
      batch_write(conn, sleep_interval, destination_table, put_requests)
      del put_requests[:]

  # flush remainder
  if len(put_requests) > 0:
    batch_write(conn, sleep_interval, destination_table, put_requests)

  # revert to original table write capacity
  update_provisioned_throughput(conn, destination_table, original_read_capacity, original_write_capacity, False)

  logging.info("Restore for " + source_table + " to " + destination_table + " table completed. Time taken: " + str(datetime.datetime.now().replace(microsecond=0) - start_time))

# parse args
parser = argparse.ArgumentParser(description="Simple DynamoDB backup/restore.")
parser.add_argument("-m", "--mode", help="'backup' or 'restore'")
parser.add_argument("-r", "--region", help="AWS region to use, e.g. 'us-west-1'. Use '" + LOCAL_REGION + "' for local DynamoDB testing.")
parser.add_argument("-s", "--srcTable", help="Source DynamoDB table name to backup or restore from, use 'tablename*' for wildcard prefix selection")
parser.add_argument("-d", "--destTable", help="Destination DynamoDB table name to backup or restore to, use 'tablename*' for wildcard prefix selection (uses '-' separator) [optional, defaults to source]")
parser.add_argument("--readCapacity", help="Change the temp read capacity of the DynamoDB table to backup from [optional]")
parser.add_argument("--writeCapacity", help="Change the temp write capacity of the DynamoDB table to restore to [defaults to " + str(RESTORE_WRITE_CAPACITY) + ", optional]")
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
start_time = datetime.datetime.now().replace(microsecond=0)
if args.mode == "backup":
  if args.srcTable.find("*") != -1:
    matching_backup_tables = get_table_name_matches(conn, args.srcTable)
    logging.info("Found " + str(len(matching_backup_tables)) + " table(s) in DynamoDB host to backup: " + ", ".join(matching_backup_tables))
    for table_name in matching_backup_tables:
      do_backup(conn, table_name, args.readCapacity)
  else:
    do_backup(conn, args.srcTable, args.readCapacity)
elif args.mode == "restore":
  if args.destTable != None:
    dest_table = args.destTable
  else:
    dest_table = args.srcTable

  if dest_table.find("*") != -1:
    matching_destination_tables = get_table_name_matches(conn, dest_table)
    logging.info("Found " + str(len(matching_destination_tables)) + " table(s) in DynamoDB host to be deleted: " + ", ".join(matching_destination_tables))
    for table_name in matching_destination_tables:
      delete_table(conn, sleep_interval, table_name)

    matching_restore_tables = get_restore_table_matches(args.srcTable)
    logging.info("Found " + str(len(matching_restore_tables)) + " table(s) in " + DUMP_PATH + " to restore: " + ", ".join(matching_restore_tables))
    for source_table in matching_restore_tables:
      do_restore(conn, sleep_interval, source_table, change_prefix(source_table, args.srcTable, dest_table), args.writeCapacity)
  else:
    delete_table(conn, sleep_interval, dest_table)
    do_restore(conn, sleep_interval, args.srcTable, dest_table, args.writeCapacity)
