#!/usr/bin/env python
import os
import shutil
import tempfile
import types
import unittest

from dynamodump import dynamodump


class TestGetRestoreTableMatches(unittest.TestCase):
    def setUp(self):
        self.dump_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dump_dir, ignore_errors=True)
        for name in ("testTable", "my-tables-one", "my-tables-two", "other-table"):
            os.mkdir(os.path.join(self.dump_dir, name))
        with open(os.path.join(self.dump_dir, ".gitkeep"), "w"):
            pass

        previous = getattr(dynamodump, "args", None)
        dynamodump.args = types.SimpleNamespace(dumpPath=self.dump_dir)
        if previous is None:
            self.addCleanup(delattr, dynamodump, "args")
        else:
            self.addCleanup(setattr, dynamodump, "args", previous)

    def matches(self, wildcard, separator="-"):
        return sorted(dynamodump.get_restore_table_matches(wildcard, separator))

    def test_star_skips_files(self):
        self.assertEqual(
            ["my-tables-one", "my-tables-two", "other-table", "testTable"],
            self.matches("*"),
        )

    def test_wildcard_with_dashes(self):
        self.assertEqual(["my-tables-one", "my-tables-two"], self.matches("my-tables*"))

    def test_wildcard_with_dash_inside_pattern(self):
        self.assertEqual(["my-tables-two"], self.matches("my-*-two"))

    def test_wildcard_prefix_without_separator(self):
        self.assertEqual(["testTable"], self.matches("test*", ""))

    def test_exact_name(self):
        self.assertEqual(["testTable"], self.matches("testTable"))
        self.assertEqual(["other-table"], self.matches("other-table"))

    def test_exact_name_of_a_file_is_not_a_table(self):
        self.assertEqual([], self.matches(".gitkeep"))

    def test_no_match(self):
        self.assertEqual([], self.matches("missing*"))
        self.assertEqual([], self.matches("missing"))


if __name__ == "__main__":
    unittest.main()
