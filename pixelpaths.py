#!/usr/bin/python

"""
This file contains different functions for iterating two-dimensionally over an image.
Each function produces an iterator of 'rows' over a given image, and each 'row' contains a iterator of (x,y) tuples
representing pixels.
However, the paths produced don't have to be necessarily actual rows or columns.
"""
from math import sqrt, tan, radians
from random import random

from util import weighted_random_choice, in_bounds, sign


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


def draw_line(start, size, slope):
    error = -1.0
    if slope > 1:
        slope = 1/slope
        switch_xy = True
    else:
        switch_xy = False
    slope_sgn = sign(slope)
    # represent change from inital x and y. If slope > 1, these are switched, since the algorithm only works when
    # the slope is less than 1.
    dx = dy = 0
    current_point = start
    x0, y0 = start
    while in_bounds((0, 0), size, current_point):
        yield current_point
        dx += 1
        error += abs(slope)
        if error > 0:
            dy += slope_sgn
            error -= 1
        current_point = (dx + x0, dy + y0) if not switch_xy else (x0 + dy, y0 + dx)


def angled_path(size, angle=0):
    if angle % 180 == 0:
        yield from horizontal_path(size)
        return
    if angle % 180 == 90:
        yield from vertical_path(size)
        return
    width, height = size
    slope = tan(radians(angle))
    start_y = 0 if slope > 0 else height - 1
    for x in range(width-1, 0, -1):
        yield draw_line((x, start_y), size, slope)
    for y in range(height):
        yield draw_line((0, y), size, slope)



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


def bresenham_circle_octant(radius):
    """
    Uses Bresenham's algorithm to draw a single octant of a circle with thickness 1,
    centered on the origin and with the given radius.
    :param radius: The radius of the circle to draw
    :return: A list of integer coordinates representing pixels.
    Starts at (radius, 0) and end with a pixel (x, y) where x == y.
    """
    x, y = radius, 0
    r2 = radius * radius
    coords = []
    while x >= y:
        coords.append((x, y))
        y += 1
        if abs((x - 1) * (x - 1) + y * y - r2) < abs(x * x + y * y - r2):
            x -= 1
    # add a point on the line x = y at the end if it's not already there.
    if coords[-1][0] != coords[-1][1]:
        coords.append((coords[-1][0], coords[-1][0]))
    return coords


def concentric_circle(center, radius, size=None):
    """
    Draws a circle with the given center and radius.
    This is designed to ensure that concentric circles with integer radii are "airtight",
    i.e. there are not unfilled pixels between them.
    :param center: The (x, y) coordinates of the center of the circle
    :param radius:
    :param size: If not None, the size of the image. This is used to skip pizxels that are out of bounds.
    :return: This is a generator that yields (x,y) coordinates of the circle one at a time
    """
    c_out = bresenham_circle_octant(radius + 1)
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
        c = x + center[0], y + center[1]
        if size is not None:
            if not in_bounds((0, 0), size, c):
                continue
        yield c


def fill_concentric_circles(size, center, radius):
    """
    Returns a path that fills a concentric circle with the given radius and center.
    :param radius:
    :param center:
    :param size: The size of the image, used to skip points that are out of bounds.
    :return: Yields iterators, where each iterator yields (x,y) coordinates of points about the circle.
    The path moves outwards from the center of the circle.
    If `size` is specified, points that are out of bounds are skipped.
    """
    for r in range(radius):
        yield concentric_circle(center, r, size=size)


def concentric_circles_path(size):
    """
    Yields a set of paths that are concentric circles, moving outwards, about the center of the image.
    :param size: The (width, height) of the image
    :return: Yields individual circles, where each circle is a generator that yields pixel coordinates. 
    """
    width, height = size
    x0, y0 = width // 2, height // 2
    max_radius = int(sqrt(2) * max(height, width))
    yield from fill_concentric_circles(radius=max_radius, center=(x0, y0), size=size)


def fill_with_circles_path(size, radius=100):
    """
    Covers an image with a set of overlapping circles of the given radius.
    :param size: The size of the image
    :param radius: The radius of the circles in question
    :return: Yields a set of filled circles that cover the whole image.
    Each circle is made up of individual concentric circles.
    """
    width, height = size
    radius = int(radius)
    dx = dy = int(2 * radius / sqrt(2))
    for x in range(dx // 2, width + dx, dx):
        for y in range(dy // 2, height + dy, dy):
            yield from fill_concentric_circles(center=(x, y), radius=radius, size=size)


def path_to_list(path):
    """
    Converts a path into a two-dimensional list of coordinates
    :param path: A path generated by the functions above, in the form of an interator over a set of rows,
    in which each row is an iterator over a set of (x, y) coordinates
    :return: A list of rows, each row a list of (x,y) coordinates
    """
    return [list(r) for r in path]


PIXEL_PATH_DICT = {
    'angled-line': angled_path,
    'circles': concentric_circles_path,
    'concentric': concentric_rectangle_path,
    'diagonal': diagonal_path,
    'diagonal-single': diagonal_single_path,
    'fill-circles': fill_with_circles_path,
    'horizontal': horizontal_path,
    'random-walk': random_walk_path,
    'random-walk-horizontal': horizontal_random_walk,
    'random-walk-vertical': vertical_random_walk,
    'vertical': vertical_path,
}
