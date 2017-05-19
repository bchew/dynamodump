import unittest

import dynamodump


class TestDynamoDumpUtils(unittest.TestCase):

    def test_calculate_limit(self):
        table_desc = dict(Table=dict(TableSizeBytes=32768, ItemCount=128))
        read_capacity = 5

        limit = dynamodump.calculate_limit(table_desc, read_capacity)

        self.assertEqual(limit, 160)

    def test_calculate_limit_empty_table(self):
        table_desc = dict(Table=dict(TableSizeBytes=0, ItemCount=0))
        read_capacity = 5

        limit = dynamodump.calculate_limit(table_desc, read_capacity)

        self.assertEqual(limit, 320)
