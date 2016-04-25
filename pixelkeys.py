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


# DIFFERENT VERSIONS OF BRIGHTNESS #

def intensity(p):
    return sum(p)/3.0


value = max


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


def hue(p):
    """
    Returns the saturation of a pixel.
    Gray pixels have saturation 0.
    :param p: A tuple of (R,G,B) values
    :return: A saturation value between
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

PIXEL_KEY_DICT = {
    'blue': blue,
    'brightness': intensity,
    'green': green,
    'hue': hue,
    'intensity': intensity,
    'lightness': lightness,
    'luma': luma,
    'red': red,
    'sum': sum,
    'value': value,
}