#!/usr/bin/python

"""
This file contains different functions for iterating two-dimensionally over an image.
Each function produces an iterator of 'rows' over a given image, and each 'row' contains a iterator of (x,y) tuples
representing pixels.
However, the paths produced don't have to be necessarily actual rows or columns.
"""

from random import random
from util import clamp


def horizontal_path(size):
    """
    Creates a generator for progressing horizontally through an image.
    :param size: A tuple (width, height) of the image size
    :return: A generator that yields a set of rows through the image.
    Each row is a generator that yields pixel coordinates.
    """
    width, height = size
    return (((x, y) for x in xrange(width)) for y in xrange(height))


def vertical_path(size):
    """
    Creates a generator for progressing vertically through an image.
    :param size: A tuple (width, height) of the image size
    :return: A generator that yields a set of columns through the image.
    Each column is a generator that yields pixel coordinates.
    """
    width, height = size
    return (((x, y) for y in xrange(height)) for x in xrange(width))


def diagonal_path(size):
    """
    Creates a set of diagonal paths moving from the top left to the bottom right of the image.
    Successive rows start at the bottom-left corner and move up until the top-right corner.
    :param size: The dimensions of the image (width, height)
    :return: A generator that yields a set of paths, each path is a set of (x,y) pixel coordinates.
    """
    width, height = size
    return (((x, x + offset) for x in range(max(0, -offset), min(width, height - offset))) for offset in
            xrange(height - 1, -width, -1))


def diagonal_single_path(size):
    """
    Creates a set of diagonal paths moving from the top left to the bottom right of the image.
    Successive rows start at the bottom-left corner and move up until the top-right corner.
    :param size: The dimensions of the image (width, height)
    :return: A generator that yields a set of paths, each path is a set of (x,y) pixel coordinates.
    """
    width, height = size

    def diagonal_path_iter():
        for offset in xrange(height - 1, -width, -1):
            for x in range(max(0, -offset), min(width, height - offset)):
                yield (x, x+offset)
    yield diagonal_path_iter()


def concentric_rectangle_path(size):
    """
    Creates a generator for progressing through an image
    :param size: A tuple (width, height) of the image size
    :return: A generator that yields a set of rows through the image.
    Each row is a generator that yields pixel coordinates.
    """

    def conc_rect_iter():
        for x in xrange(min_x, max_x):
            yield (x, min_y)
        for y in xrange(min_y + 1, max_y):
            yield (max_x - 1, y)
        for x in xrange(max_x - 2, min_x - 1, -1):
            yield (x, max_y - 1)
        for y in xrange(max_y - 2, min_y, -1):
            yield (min_x, y)

    width, height = size
    min_x, max_x = 0, width
    min_y, max_y = 0, height

    while min_x < max_x and min_y < max_y:
        yield conc_rect_iter()

        min_x += 1
        min_y += 1
        max_x -= 1
        max_y -= 1


def random_walk_path(size):
    """
    A generator that yields random walks from the left to the right of an image.
    :param size: A tuple (width, height) of the image size
    :return: A generator that returns a set of random walks through the image.
    Each random walk is an iterator if tuples (x,y) of pixels moving horizontally across the image.
    """

    def random_walk_iter(y_tmp):
        for x in xrange(width):
            yield (x, y_tmp)
            r = random()
            p = 0.5
            if r >= p:
                y_tmp += 1
            else:
                y_tmp -= 1
            y_tmp = clamp(y_tmp, 0, height - 1)

    width, height = size
    for y in xrange(height):
        yield random_walk_iter(y)


PIXEL_PATH_DICT = {
    'concentric': concentric_rectangle_path,
    'diagonal': diagonal_path,
    'diagonal-single': diagonal_single_path,
    'horizontal': horizontal_path,
    'random-walk': random_walk_path,
    'vertical': vertical_path,
}
