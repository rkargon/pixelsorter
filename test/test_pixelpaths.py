#!/usr/bin/python

import unittest

from pixelpaths import horizontal_path, vertical_path, diagonal_path, diagonal_single_path, path_to_list, \
    concentric_rectangle_path


class TestPixelPaths(unittest.TestCase):
    def test_horizontal_path(self):
        p = horizontal_path((4, 4))
        p_list = path_to_list(p)
        rows = [[(x, y) for x in range(4)] for y in range(4)]
        self.assertListEqual(p_list, rows)

    def test_vertical_path(self):
        p = vertical_path((4, 4))
        p_list = path_to_list(p)
        cols = [[(x, y) for y in range(4)] for x in range(4)]
        self.assertListEqual(p_list, cols)

    def test_diagonal_path(self):
        # test square image
        p = diagonal_path((4, 4))
        p_list = path_to_list(p)
        test_list = [[(0, 3)],
                     [(0, 2), (1, 3)],
                     [(0, 1), (1, 2), (2, 3)],
                     [(0, 0), (1, 1), (2, 2), (3, 3)],
                     [(1, 0), (2, 1), (3, 2)],
                     [(2, 0), (3, 1)],
                     [(3, 0)]]
        self.assertListEqual(p_list, test_list)

        # test landscape-dimensioned image
        p = diagonal_path((4, 2))
        p_list = path_to_list(p)
        test_list = [[(0, 1)],
                     [(0, 0), (1, 1)],
                     [(1, 0), (2, 1)],
                     [(2, 0), (3, 1)],
                     [(3, 0)]]
        self.assertListEqual(p_list, test_list)

        # test portrait-dimensioned image
        p = diagonal_path((2, 4))
        p_list = [list(r) for r in p]
        test_list = [[(0, 3)],
                     [(0, 2), (1, 3)],
                     [(0, 1), (1, 2)],
                     [(0, 0), (1, 1)],
                     [(1, 0)]]
        self.assertListEqual(p_list, test_list)

    def test_diagonal_single_path(self):
        # test square image
        p = diagonal_single_path((4, 4))
        p_list = path_to_list(p)
        test_list = [[(0, 3),
                     (0, 2), (1, 3),
                     (0, 1), (1, 2), (2, 3),
                     (0, 0), (1, 1), (2, 2), (3, 3),
                     (1, 0), (2, 1), (3, 2),
                     (2, 0), (3, 1),
                     (3, 0)]]
        self.assertListEqual(p_list, test_list)

    def test_concentric_rectangle_path(self):
        # landscape proportions
        p = concentric_rectangle_path((4, 3))
        p_list = path_to_list(p)
        test_list = [[(0, 0), (1, 0), (2, 0), (3, 0),
                     (3, 1), (3, 2),
                     (2, 2), (1, 2), (0, 2),
                     (0, 1)],
                     [(1, 1), (2, 1)]]
        self.assertListEqual(p_list, test_list)

        # portrait proportions
        p = concentric_rectangle_path((3, 4))
        p_list = path_to_list(p)
        test_list = [[(0, 0), (1, 0), (2, 0),
                     (2, 1), (2, 2), (2, 3),
                     (1, 3), (0, 3),
                     (0, 2), (0, 1)],
                     [(1, 1), (1, 2)]]
        self.assertListEqual(p_list, test_list)
