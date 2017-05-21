import unittest
import mock

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


class TestRateLimiter(unittest.TestCase):

    @mock.patch('time.sleep')
    def test_rate_limiter(self, sleep):
        with mock.patch('time.time', return_value=10.0):
            rate_limiter = dynamodump.RateLimiter(5)

        with mock.patch('time.time', return_value=11.0):
            rate_limiter.acquire(10)

        self.assertEqual(rate_limiter.consumed_permits, 10)
        sleep.assert_called_once_with(1)
