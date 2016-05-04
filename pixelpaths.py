#!/usr/bin/python

"""
This file contains different functions for iterating two-dimensionally over an image.
Each function produces an iterator of 'rows' over a given image, and each 'row' contains a iterator of (x,y) tuples
representing pixels.
However, the paths produced don't have to be necessarily actual rows or columns.
"""
from random import random

from util import weighted_random_choice


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
                yield (x, x + offset)

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


def random_walk_path(size, distribution=None, start_points=None):
    """
    Performs random walks as a markov chain with an arbitrary distribution and start points
    :param size: The size of the image as (width, height)
    :param distribution: A hash of {(dx, dy): probability} the distribution
    that describes how the random walk moves to neighboring states. This does not need to be normalized to sum to 1.
    Both dx and dy should be one of [-1, 0, 1].
     By default, this is a uniform distribution over all adjacent states.
    :param start_points: A set of starting points for each random walk.
    By default, these are 10 random points in the image.
    :return: An iterator of paths, with each path being an iterator of (x,y) pixels
    """

    # TODO allow non-adjacent neighbors also?

    def random_walk_iter(start_pt):
        x, y = start_pt
        while True:
            dx, dy = weighted_random_choice(distribution.iteritems())
            x += dx
            y += dy
            if x < 0 or x >= width or y < 0 or y >= height:
                return
            yield (x, y)

    width, height = size
    neighbors = [(dx, dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if dy != 0 or dx != 0]
    if distribution is None:
        distribution = {n: 0.125 for n in neighbors}
    else:
        for n in neighbors:
            if n not in distribution:
                distribution[n] = 0
        neighbor_sum = sum(distribution[n] for n in neighbors)
        if neighbor_sum <= 0:
            raise ValueError("Distribution must be positive, nonzero for adjacent neighbors")
        else:
            distribution = {n: p / float(neighbor_sum) for n, p in distribution.iteritems()}
    if start_points is None:
        start_points = [(int(random() * width), int(random() * height)) for _ in xrange(10)]

        # # by default, just start at each pixel on the left edge of the image
        # start_points = [(0, y) for y in xrange(height)]

    for x0, y0 in start_points:
        yield random_walk_iter((x0, y0))


def horizontal_random_walk(size):
    """
    Generates random walks that start at the left side of the image and move towards the right
    :param size: The size of the image
    :return: An iterator of paths, each an iterator of (x,y) coordinates
    """
    _, height = size
    distribution = {(1, dy): 1 / 3.0 for dy in [-1, 0, 1]}
    start_points = [(0, y) for y in xrange(height)]
    return random_walk_path(size, distribution, start_points)


def vertical_random_walk(size):
    """
    Generates random walks that start at the left side of the image and move towards the right
    :param size: The size of the image
    :return: An iterator of paths, each an iterator of (x,y) coordinates
    """
    width, _ = size
    distribution = {(dx, 1): 1 / 3.0 for dx in [-1, 0, 1]}
    start_points = [(x, 0) for x in xrange(width)]
    return random_walk_path(size, distribution, start_points)


PIXEL_PATH_DICT = {
    'concentric': concentric_rectangle_path,
    'diagonal': diagonal_path,
    'diagonal-single': diagonal_single_path,
    'horizontal': horizontal_path,
    'random-walk': random_walk_path,
    'random-walk-horizontal': horizontal_random_walk,
    'random-walk-vertical': vertical_random_walk,
    'vertical': vertical_path,
}
