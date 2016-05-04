
"""
Math and other utility functions
"""
from math import floor
from random import random


def clamp(x, a, b):
    """
    Clamps a value x between a minimum a and a maximum b
    :param x: The value to clamp
    :param a: The minimum
    :param b: The maximum
    :return: The clamped value
    """
    return max(a, min(x, b))


def coords_to_index(coords, width):
    """
    Converts x,y coordinates of an image (with (0,0) in in the top-left corner) to an index
     in a 1-D array of pixels
    :param coords: A tuple (x,y)
    :param width: The width of the image
    :return: The index of the corresponding pixel
    """
    return coords[1] * width + coords[0]


def index_to_coords(index, width):
    """
    Converts an index in an array of pixels to an x, y coordinate given an image width.
    :param index: The index in the array
    :param width: The width of the image
    :return: (x,y) coordinate of the pixels specified by `index`
    """
    return index % width, floor(index / width)


def weighted_random_choice(items):
    """
    Returns a weighted random choice from a list of items.
    :param items: A list of tuples (object, weight)
    :return: A random object, whose likelihood is proportional to its weight.
    """
    l = list(items)
    r = random() * sum([i[1] for i in l])
    for x, p in l:
        if p > r:
            return x
        r -= p
    return None
