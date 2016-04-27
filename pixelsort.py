#!/usr/bin/python
import argparse
from random import randint

from PIL import Image

from pixelkeys import PIXEL_KEY_DICT
from pixelpaths import vertical_path, horizontal_path, PIXEL_PATH_DICT
from util import coords_to_index


def sort_pixels(pixels, size, vertical=False, path=None, max_interval=100, progressive_amount=0, randomize=False,
                key=None, discretize=0, reverse=False):
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
    if path is None:
        if vertical:
            pixel_iterator = vertical_path(size)
        else:
            pixel_iterator = horizontal_path(size)
    else:
        pixel_iterator = path(size)

    # check if interval should increase progressively through image
    if progressive_amount > 0:
        current_max_interval = max_interval * progressive_amount
    else:
        current_max_interval = max_interval

    # for each path
    for path in pixel_iterator:
        path_finished = False
        # traverse path until it is finished
        while not path_finished:
            if progressive_amount > 0:
                current_max_interval += max_interval * progressive_amount

            if randomize and current_max_interval > 0:
                interval = randint(1, int(current_max_interval)+1)
            else:
                interval = current_max_interval

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


def main():
    # set up command line argument parser
    parser = argparse.ArgumentParser(description='A tool for pixel-sorting images')
    parser.add_argument("infile", help="The input image")
    parser.add_argument("-o", "--outfile", required=True, help="The output image")
    parser.add_argument("-d", "--discretize", type=int, default=0,
                        help="Divides float values of pixels by the given integer amount, and casts to an int. "
                             "Used to bin pixel values into several discrete categories.")
    parser.add_argument("-i", "--interval", type=int, default=0,
                        help="The size of each sorting interval, in pixels. If 0, whole row is sorted.")
    parser.add_argument("-p", "--path", type=str, default="",
                        help="The type of path used to sort over the image. Horizontal by default.")
    parser.add_argument("--progressive-amount", type=float, default=0,
                        help="How fast interval size should increase as one moves through the image. "
                             "This is a ratio of the max interval size.")
    parser.add_argument("-r", "--randomize", action='store_true', default=False,
                        help="Whether to randomize pixel-sorting intervals")
    parser.add_argument("-R", "--reverse", action='store_true', default=False,
                        help="Whether to reverse pixel-sorting order")
    parser.add_argument("-s", "--sortkey", type=str, default="", help="Function applied to pixels to sort them.")
    parser.add_argument("-v", "--vertical", action='store_true', default=False,
                        help="Whether to pixel-sort vertically instead of horizontally")
    args = parser.parse_args()

    # load image
    img = Image.open(args.infile)
    original_pixels = list(img.getdata())

    key = PIXEL_KEY_DICT.get(args.sortkey.lower(), None)
    path = PIXEL_PATH_DICT.get(args.path.lower(), None)
    out_pixels = sort_pixels(original_pixels, img.size, randomize=args.randomize, vertical=args.vertical, path=path,
                             max_interval=args.interval, progressive_amount=args.progressive_amount, discretize=args.discretize, reverse=args.reverse, key=key)

    # write output image
    img_out = Image.new(img.mode, img.size)
    img_out.putdata(out_pixels)
    img_out.save(args.outfile)


if __name__ == '__main__':
    main()
