#!/usr/bin/python
import argparse
from random import randint

from PIL import Image

from pixelkeys import PIXEL_KEY_DICT


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


def coords_to_index(coords, width):
    """
    Converts x,y coordinates of an image (with (0,0) in in the top-left corner) to an index
     in a 1-D array of pixels
    :param coords: A tuple (x,y)
    :param width: The width of the image
    :return: The index of the corresponding pixel
    """
    return coords[1] * width + coords[0]


def sort_pixels(pixels, size, vertical=False, max_interval=100, randomize=False, key=None, discretize=0, reverse=False):
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

    out_pixels = list(pixels)
    width, height = size

    if discretize > 0:
        sort_key = lambda p: int(key(p)/discretize)
    else:
        sort_key = key

    # select path to go through image
    # pixel_iterator is an iterator that returns a set of different 'lines', or 'rows' through the image.
    #   Each line is itself an iterator that returns a set of coordinates of pixels in the image.
    if vertical:
        pixel_iterator = vertical_path(size)
    else:
        pixel_iterator = horizontal_path(size)

    # for each path
    for path in pixel_iterator:
        path_finished = False
        # traverse path until it is finished
        while not path_finished:
            if randomize and max_interval > 0:
                interval = randint(1, max_interval)
            else:
                interval = max_interval

            # get pixel coordinates of path
            px_indices = []
            i = 0
            # if interval is 0, just sort whole line at once
            while i < interval or interval == 0:
                try:
                    coords = path.next()
                except StopIteration:
                    path_finished = True
                    break
                px_indices.append(coords_to_index(coords, width))
                i += 1

            # sort pixels, apply to output image
            sorted_pixels = sorted([pixels[i] for i in px_indices], key=sort_key, reverse=reverse)
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
    parser = argparse.ArgumentParser(description='A tool for pixel-sorting images')
    parser.add_argument("infile", help="The input image")
    parser.add_argument("-o", "--outfile", required=True, help="The output image")
    parser.add_argument("-d", "--discretize", type=int, default=0,
                        help="Divides float values of pixels by the given integer amount, and casts to an int. "
                             "Used to bin pixel values into several discrete categories.  ")
    parser.add_argument("-i", "--interval", type=int, default=0,
                        help="The size of each sorting interval, in pixels. If 0, whole row is sorted.")
    parser.add_argument("-r", "--randomize", action='store_true', default=False,
                        help="Whether to randomize pixel-sorting intervals")
    parser.add_argument("-R", "--reverse", action='store_true', default=False,
                        help="Whether to reverse pixel-sorting order")
    parser.add_argument("-s", "--sortkey", type=str, default=None, help="Function applied to pixels to sort them.")
    parser.add_argument("-v", "--vertical", action='store_true', default=False,
                        help="Whether to pixel-sort vertically instead of horizontally")
    args = parser.parse_args()

    # load image
    img = Image.open(args.infile)
    original_pixels = list(img.getdata())

    key = PIXEL_KEY_DICT.get(args.sortkey.lower(), None)
    out_pixels = sort_pixels(original_pixels, img.size, randomize=args.randomize, vertical=args.vertical,
                             max_interval=args.interval, discretize=args.discretize, reverse=args.reverse, key=key)

    # write output image
    img_out = Image.new(img.mode, img.size)
    img_out.putdata(out_pixels)
    img_out.save(args.outfile)


if __name__ == '__main__':
    main()
