#!/usr/bin/python

import unittest

from util import *


class TestUtils(unittest.TestCase):
    def test_sign(self):
        self.assertEqual(1, sign(2))
        self.assertEqual(-1, sign(-2))
        self.assertEqual(0, sign(0))

    def test_clamp(self):
        c = clamp(5, 0, 100)
        self.assertEqual(c, 5)

        c = clamp(-10, 0, 100)
        self.assertEqual(c, 0)

        c = clamp(1000, 0, 100)
        self.assertEqual(c, 100)

    def test_coords_to_index(self):
        w = 100
        c = (40, 10)
        i = coords_to_index(coords=c, width=w)
        self.assertEqual(i, 1040)

    def test_index_to_coords(self):
        i = 1040
        w = 100
        c = index_to_coords(index=i, width=w)
        self.assertEqual(c, (40, 10))

    def test_in_bounds(self):
        min_b = (10, 10)
        max_b = (100, 100)
        out_of_bounds_coords = [(-10, y) for y in [-10, 50, 110]]
        out_of_bounds_coords += [(x, -10) for x in [-10, 50, 110]]
        out_of_bounds_coords += [(110, y) for y in [-10, 50, 110]]
        out_of_bounds_coords += [(x, 110) for x in [-10, 50, 110]]
        in_bounds_coords = [(50, y) for y in [10, 50, 99]]
        in_bounds_coords += [(x, 50) for x in [10, 50, 99]]
        self.assertFalse(any([in_bounds(min_b=min_b, max_b=max_b, point=p) for p in out_of_bounds_coords]),
                         msg = "Some out of bounds coordinates were in bounds.")
        self.assertTrue(all([in_bounds(min_b=min_b, max_b=max_b, point=p) for p in in_bounds_coords]),
                        msg="Some in-bounds coordinates were out of bounds.")
        # max coord value is out of bounds. (think range semantics)
        self.assertFalse(in_bounds(min_b, max_b, (10, 100)))
