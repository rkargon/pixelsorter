#!/usr/bin/python
from random import randint, random
import sys

from PIL import Image


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


def concentric_rectangle_path(size):
    """
    Creates a generator for progressing through an image
    :param size: A tuple (width, height) of the image size
    :return: A generator that yields a set of rows through the image.
    Each row is a generator that yields pixel coordinates.
    """
    # TODO don't make this a single path / spiral
    def conc_rect_iter(min_x, max_x, min_y, max_y):
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
        yield conc_rect_iter(min_x, max_x, min_y, max_y)

        min_x += 1
        min_y += 1
        max_x -= 1
        max_y -= 1



def coords_to_index(coords, width):
    """
    Converts x,y coordinates of an image (with (0,0) in in the top-left corner) to an index
     in a 1-D array of pixels
    :param coords: A tuple (x,y)
    :param width: The width of the image
    :return: The index of the corresponding pixel
    """
    return coords[1]*width + coords[0]


def sort_pixels(pixels, size, vertical=False, max_interval=100, randomize=False, key=None, reverse=False):
    """
    Given an image as a list of pixels, applies pixel sorting and returns the new pixels
    :param pixels: A list of tuples (R,G,B) representing the pixels of the image
    :param size: The size of the image as a tuple (width, height)
    :param vertical: Whether or not the color sorting is applied vertically (the default is horizontal)
    :param max_interval: The largest interval of adjacent pixels to sort
    :param randomize: Whether to use random intervals of pixels
    :param key: The function to use for sorting, e.g. brightness or red amount.
                This function takes a pixel and returns a value to be sorted.
    :param reverse: Whether or not to reverse the direction of the sorting
    :return: The pixels of the resulting image as a list of (R,G,B) tuples
    """
    #TODO get HSV values, other color spaces/profiles/models/whatever
    out_pixels = list(pixels)
    width, height = size

    # TODO more types of paths, not just horizontal/vertical
    # select path to go through image
    # pixel_iterator is an iterator that returns a set of different 'lines', or 'rows' through the image.
    #   Each line is itself an iterator that returns a set of coordinates of pixels in the image.
    if vertical:
        pixel_iterator = vertical_path(size)
    else:
        pixel_iterator = horizontal_path(size)
    pixel_iterator = concentric_rectangle_path(size)

    # for each path
    for path in pixel_iterator:
        path_finished = False
        # traverse path until it is finished
        while not path_finished:
            if randomize:
                interval = randint(1, max_interval)
            else:
                interval = max_interval

            # get pixel coordinates of path
            px_indices = []
            for i in xrange(interval):
                try:
                    coords = path.next()
                except StopIteration:
                    path_finished = True
                    break
                px_indices.append(coords_to_index(coords, width))

            # sort pixels, apply to output image
            sorted_pixels = sorted([pixels[i] for i in px_indices], key=key, reverse=reverse)
            for i in xrange(len(px_indices)):
                index = px_indices[i]
                pixel = sorted_pixels[i]
                out_pixels[index] = pixel
    return out_pixels


def clamp(x, a, b):
    """
    Clamps a value x between a minimum a and a maximum b
    :param x: The value to clamp
    :param a: The minimum
    :param b: The maximum
    :return: The clamped value
    """
    return max(a, min(x, b))

def main():
    imgfile, outfile = sys.argv[1:]

    # load image
    img = Image.open(imgfile)
    original_pixels = list(img.getdata())

    out_pixels = sort_pixels(original_pixels, img.size, vertical=True, max_interval=500, key=sum)

    # write output image
    img_out = Image.new(img.mode, img.size)
    img_out.putdata(out_pixels)
    img_out.save(outfile)


if __name__ == '__main__':
    main()
