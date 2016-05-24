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
    return (((x, y) for x in range(width)) for y in range(height))


def vertical_path(size):
    """
    Creates a generator for progressing vertically through an image.
    :param size: A tuple (width, height) of the image size
    :return: A generator that yields a set of columns through the image.
    Each column is a generator that yields pixel coordinates.
    """
    width, height = size
    return (((x, y) for y in range(height)) for x in range(width))


def angled_path(size):
    width, height = size


def diagonal_path(size):
    """
    Creates a set of diagonal paths moving from the top left to the bottom right of the image.
    Successive rows start at the bottom-left corner and move up until the top-right corner.
    :param size: The dimensions of the image (width, height)
    :return: A generator that yields a set of paths, each path is a set of (x,y) pixel coordinates.
    """
    width, height = size
    return (((x, x + offset) for x in range(max(0, -offset), min(width, height - offset))) for offset in
            range(height - 1, -width, -1))


def diagonal_single_path(size):
    """
    Creates a set of diagonal paths moving from the top left to the bottom right of the image.
    Successive rows start at the bottom-left corner and move up until the top-right corner.
    :param size: The dimensions of the image (width, height)
    :return: A generator that yields a set of paths, each path is a set of (x,y) pixel coordinates.
    """
    width, height = size

    def diagonal_path_iter():
        for offset in range(height - 1, -width, -1):
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
        for x in range(min_x, max_x):
            yield (x, min_y)
        # if rectangle only has height of 1, prevent path from doubling back along x
        if min_y + 1 == max_y:
            return
        for y in range(min_y + 1, max_y):
            yield (max_x - 1, y)
        for x in range(max_x - 2, min_x - 1, -1):
            yield (x, max_y - 1)
        for y in range(max_y - 2, min_y, -1):
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
            dx, dy = weighted_random_choice(iter(distribution.items()))
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
            distribution = {n: p / float(neighbor_sum) for n, p in distribution.items()}
    if start_points is None:
        start_points = [(int(random() * width), int(random() * height)) for _ in range(10)]

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
    start_points = [(0, y) for y in range(height)]
    return random_walk_path(size, distribution, start_points)


def vertical_random_walk(size):
    """
    Generates random walks that start at the left side of the image and move towards the right
    :param size: The size of the image
    :return: An iterator of paths, each an iterator of (x,y) coordinates
    """
    width, _ = size
    distribution = {(dx, 1): 1 / 3.0 for dx in [-1, 0, 1]}
    start_points = [(x, 0) for x in range(width)]
    return random_walk_path(size, distribution, start_points)


def concentric_circles_path(size):
    """
    Yields a set of paths that are concentric circles, moving outwards, about the center of the image.
    :param size: The (width, height) of the image
    :return: Yields individual circles, where each circle is a generator that yields pixel coordinates. 
    """

    def bresenham_circle_octant(radius):
        """
        Uses Bresenham's algorithm to draw a single octant of a circle with thickness 1,
        centered on the origin and with the given radius.
        :param radius: The radius of the circle to draw
        :return: A list of integer coordinates representing pixels.
        Starts at (radius, 0) and end with a pixel (x, y) where x == y.
        """
        x, y = radius, 0
        r2 = radius*radius
        coords = []
        while x >= y:
            coords.append((x, y))
            y += 1
            if abs((x-1)*(x-1) + y*y - r2) < abs(x*x + y*y - r2):
                x -= 1
        # add a point on the line x = y at the end if it's not already there.
        if coords[-1][0] != coords[-1][1]:
            coords.append((coords[-1][0], coords[-1][0]))
        return coords

    def concentric_circle(center, radius):
        """
        Draws a circle with the given center and radius.
        This is designed to ensure that concentric circles with integer radii are "aritight",
        i.e. there are not unfilled pixels between them.
        :param center: The (x, y) coordinates of the center of the circle
        :param radius:
        :return: This is a generator that yields (x,y) coordinates of the circle one at a time
        """
        c_out = bresenham_circle_octant(radius+1)
        c_in = bresenham_circle_octant(radius)
        coords = []

        # note that in this loop, y also serves as the array index,
        # since it starts at 0 and increments each element.
        for x, y in c_in:
            for x1 in range(x, c_out[y][0]):
                coords.append((x1, y))
        # copy octant 8 times to get other pixels
        # TODO might recount pixels where x == y
        next_octant = [(y, x) for x, y in reversed(coords)]
        coords.extend(next_octant)
        next_quadrant = [(-y, x) for x, y in coords]
        coords.extend(next_quadrant)
        next_half = [(-x, -y) for x, y in coords]
        coords.extend(next_half)

        for x, y in coords:
            yield x+center[0], y+center[1]

    width, height = size
    start_x, start_y = width//2, height//2
    for r in range(height - start_y):
        yield concentric_circle((start_x, start_y), r)



def path_to_list(path):
    """
    Converts a path into a two-dimensional list of coordinates
    :param path: A path generated by the functions above, in the form of an interator over a set of rows,
    in which each row is an iterator over a set of (x, y) coordinates
    :return: A list of rows, each row a list of (x,y) coordinates
    """
    return [list(r) for r in path]

PIXEL_PATH_DICT = {
    'circles': concentric_circles_path,
    'concentric': concentric_rectangle_path,
    'diagonal': diagonal_path,
    'diagonal-single': diagonal_single_path,
    'horizontal': horizontal_path,
    'random-walk': random_walk_path,
    'random-walk-horizontal': horizontal_random_walk,
    'random-walk-vertical': vertical_random_walk,
    'vertical': vertical_path,
}
