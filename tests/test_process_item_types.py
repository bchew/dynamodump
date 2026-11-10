#!/usr/bin/env python
import copy
import json
import unittest

from dynamodump import dynamodump


def round_trip(items):
    """Serialize items the way backup does, then decode them the way restore does."""
    dumped = json.dumps({"Items": items})
    loaded = json.loads(dumped)
    dynamodump.process_item_types(loaded)
    return loaded["Items"]


class TestProcessItemTypes(unittest.TestCase):
    def assert_round_trip(self, items):
        expected = copy.deepcopy(items)
        self.assertEqual(expected, round_trip(items))

    def test_top_level_binary(self):
        self.assert_round_trip([{"id": {"S": "1"}, "b": {"B": b"\x00\x01\xff"}}])

    def test_binary_in_map(self):
        self.assert_round_trip(
            [{"id": {"S": "1"}, "m": {"M": {"b": {"B": b"\x00\x01\xff"}}}}]
        )

    def test_binary_in_list(self):
        self.assert_round_trip(
            [{"id": {"S": "1"}, "l": {"L": [{"S": "x"}, {"B": b"\x00\x01\xff"}]}}]
        )

    def test_binary_in_list_inside_map(self):
        self.assert_round_trip(
            [
                {
                    "id": {"S": "1"},
                    "m": {
                        "M": {
                            "l": {"L": [{"B": b"\x02\x03"}, {"N": "5"}]},
                            "s": {"S": "text"},
                        }
                    },
                }
            ]
        )

    def test_map_inside_list_inside_map(self):
        self.assert_round_trip(
            [{"m": {"M": {"l": {"L": [{"M": {"b": {"B": b"\xde\xad\xbe\xef"}}}]}}}}]
        )

    def test_binary_set(self):
        self.assert_round_trip(
            [{"id": {"S": "1"}, "bs": {"BS": [b"\x00\x01", b"\xfe\xff"]}}]
        )

    def test_binary_set_nested(self):
        self.assert_round_trip(
            [{"m": {"M": {"l": {"L": [{"BS": [b"\x00\x01", b"\xfe\xff"]}]}}}}]
        )

    def test_other_types_untouched(self):
        self.assert_round_trip(
            [
                {
                    "s": {"S": "abc"},
                    "n": {"N": "1"},
                    "ns": {"NS": ["1", "2"]},
                    "ss": {"SS": ["a", "b"]},
                    "bool": {"BOOL": True},
                    "null": {"NULL": True},
                    "m": {"M": {"s": {"S": "abc"}, "ns": {"NS": ["3"]}}},
                    "l": {"L": [{"SS": ["x"]}, {"N": "9"}]},
                }
            ]
        )


if __name__ == "__main__":
    unittest.main()
