#!/usr/bin/python
import random
"""
This contains different functions applies to pixel values before sorting.
"""


def red(p):
    return p[0]


def green(p):
    return p[1]


def blue(p):
    return p[2]


# DIFFERENT VERSIONS OF BRIGHTNESS #

def intensity(p):
    return sum(p)/3.0


def lightness(p):
    return (max(p) + min(p))/2.0


def luma(p):
    """
    Returns brightness of a pixel, based on relative luminance
    This is based on ITU-R BT.709. Note that human eyes are most sensitive to green light.
    :param p: A tuple of (R,G,B) values
    :return: The relative luminance of a pixel (in the range [0, 255]).
    """
    return 0.2126*p[0] + 0.7152*p[1] + 0.0722*p[2]


def chroma(p):
    return max(p) - min(p)


def hue(p):
    """
    Returns the saturation of a pixel.
    Gray pixels have saturation 0.
    :param p: A tuple of (R,G,B) values
    :return: A saturation value between 0 and 360
    """
    min_c = min(p)
    max_c = max(p)
    d = float(max_c - min_c)
    if d == 0:
        return 0

    if max_c == p[0]:
        h = (p[1] - p[2]) / d
    elif max_c == p[1]:
        h = 2 + (p[2] - p[0]) / d
    else:
        h = 4 + (p[0] - p[1]) / d
    h *= 60
    if h < 0:
        h += 360
    return h


def saturation(p):
    """
    Returns the saturation of a pixel, defined as the ratio of chroma to value.
    :param p: A tuple of (R,G,B) values
    :return: The saturation of a pixel, from 0 to 1
    """
    max_c = max(p)
    min_c = min(p)
    if max_c == 0:
        return 0
    return (max_c - min_c) / float(max_c)


def randomval(p):
    """
    Returns a random float in (0,1)
    :param p: A tuple of (R,G,B) values
    :return: A random float, from 0 to 1
    """
    return random.random()

PIXEL_KEY_DICT = {
    'blue': blue,
    'brightness': intensity,
    'chroma': chroma,
    'green': green,
    'hue': hue,
    'intensity': intensity,
    'lightness': lightness,
    'luma': luma,
    'red': red,
    'saturation': saturation,
    'sum': sum,
    'value': max,
    'random': randomval,
}