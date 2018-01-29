#!/usr/bin/env python
import json
import unittest

TEST_DATA_PATH = "test/testTable"
DUMP_DATA_PATH = "dump/testRestoredTable"
SCHEMA_FILE = "schema.json"
DATA_FILE = "0001.json"


class TestDynamoDump(unittest.TestCase):

    def setUp(self):
        with open(TEST_DATA_PATH + "/" + SCHEMA_FILE, 'r') as f:
            data = f.read()
        self.test_table_schema = json.loads(data)

        with open(DUMP_DATA_PATH + "/" + SCHEMA_FILE, 'r') as f:
            data = f.read()
        self.restored_test_table_schema = json.loads(data)

        with open(TEST_DATA_PATH + "/data/" + DATA_FILE, 'r') as f:
            data = f.read()
        self.test_table_data = json.loads(data)

        with open(DUMP_DATA_PATH + "/data/" + DATA_FILE, 'r') as f:
            data = f.read()
        self.restored_test_table_data = json.loads(data)

    def test_schema(self):
        self.assertEqual(self.test_table_schema["Table"]["AttributeDefinitions"],
                         self.restored_test_table_schema["Table"]["AttributeDefinitions"])
        self.assertEqual(self.test_table_schema["Table"]["ProvisionedThroughput"]["WriteCapacityUnits"],
                         self.restored_test_table_schema["Table"]["ProvisionedThroughput"]["WriteCapacityUnits"])
        self.assertEqual(self.test_table_schema["Table"]["ProvisionedThroughput"]["ReadCapacityUnits"],
                         self.restored_test_table_schema["Table"]["ProvisionedThroughput"]["ReadCapacityUnits"])
        self.assertEqual(self.test_table_schema["Table"]["KeySchema"],
                         self.restored_test_table_schema["Table"]["KeySchema"])
        self.assertEqual(self.test_table_schema["Table"]["TableSizeBytes"],
                         self.restored_test_table_schema["Table"]["TableSizeBytes"])
        self.assertEqual("testRestoredTable",
                         self.restored_test_table_schema["Table"]["TableName"])
        self.assertEqual(self.test_table_schema["Table"]["TableStatus"],
                         self.restored_test_table_schema["Table"]["TableStatus"])
        self.assertEqual(self.test_table_schema["Table"]["ItemCount"],
                         self.restored_test_table_schema["Table"]["ItemCount"])

    def test_data(self):
        self.assertEqual(self.test_table_data, self.restored_test_table_data)


if __name__ == '__main__':
    unittest.main()
