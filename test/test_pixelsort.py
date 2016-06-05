#!/usr/bin/python

import unittest

from pixelsort import *


class TestPixelSort(unittest.TestCase):
    def test_parse_arg_type(self):
        # returns non-string arguments directly
        non_string_vals = [None, 1, 1.0, False, (4, 5), [1, 2]]
        for v in non_string_vals:
            self.assertIs(parse_arg_type(v), v)

        # string parsing
        self.assertIs(parse_arg_type("owls"), "owls")
        self.assertIs(parse_arg_type("4"), 4)

        # float identity is weird, sometimes 4.4 'is not' 4.4
        self.assertIs(type(parse_arg_type("4.4")), float)
        self.assertEqual(parse_arg_type("4.4"), 4.4)

        self.assertIs(parse_arg_type("true"), True)
        self.assertIs(parse_arg_type("True"), True)
        self.assertIs(parse_arg_type("false"), False)
        self.assertIs(parse_arg_type("False"), False)
        pass
