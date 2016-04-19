#!/usr/bin/python

"""
This contains different functions applies to pixel values before sorting.
"""


def red(p):
    return p[0]


def green(p):
    return p[1]


def blue(p):
    return p[2]


def brightness(p):
    """
    Returns brightness of a pixel, based on relative luminance
    This is based on ITU-R BT.709. Note that human eyes are most sensitive to green light.
    :param p: A tuple of (R,G,B) values
    :return: The relative luminance of a pixel (in the range [0, 255]).
    """
    return 0.2126*p[0] + 0.7152*p[1] + 0.0722*p[2]

PIXEL_KEY_DICT = {
    'blue': blue,
    'brightness': brightness,
    'green': green,
    'red': red,
    'sum': sum,
}