#!/usr/bin/python
import argparse
from random import randint, random

from PIL import Image

from pixelkeys import PIXEL_KEY_DICT
from pixelpaths import vertical_path, horizontal_path, PIXEL_PATH_DICT
from util import coords_to_index


def sort_pixels(pixels, size, vertical=False, path=None, max_interval=100, progressive_amount=0, randomize=False,
                key=None, discretize=0, reverse=False):
    """
    Given an image as a list of pixels, applies pixel sorting and returns the new pixels
    :param discretize: Amount by which to "discretize" pixel values. This is done by dividing each pixel's value
    (after applying the sort key) by the given amount and then converting to an integer.
    This would mean that pixels are "binned" into discrete categories, and sorting would be different.
    Since sorting is stable, this means that pixels with low-level noise remain grouped together,
    and small details can be preserved in sorting.
    :param progressive_amount: If this is non-zero,
    then the sorting interval increases as one progresses row-by-row through the image.
    progressive_amount indicates the amount, in pixels, by which to increase the sorting interval after each row.
    :param path: The specific path used to iterate through the image.
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

    if discretize > 0 and key is not None:
        def sort_key(p): return int(key(p) / discretize)
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
                interval = randint(1, int(current_max_interval) + 1)
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


def get_tile_from_image(image, size, top_left_corner, tile_size):
    """
    Returns a rectangular region of the given image as a separate image
    If the tile goes off the edge of the image, it will be truncated. The new size is also returned.
    :param image: The given image, as a list of (R,G,B) tuples
    :param size: The size of the image, as (width, height)
    :param top_left_corner: The top left corner of the tile, relative to the image, as a tuple (x,y)
    :param tile_size: The size of the tile, as a tuple (width, height)
    :return: A tuple (tile, size) where the tile is a list of (R,G,B) tuples and the size is (width, height)
    """
    tile_pixels = []
    # crop tile if necessary
    tile_x = min(size[0] - top_left_corner[0], tile_size[0])
    tile_y = min(size[1] - top_left_corner[1], tile_size[1])
    tile_size = tile_x, tile_y
    for y in xrange(tile_size[1]):
        for x in xrange(tile_size[0]):
            coords = (x + top_left_corner[0], y + top_left_corner[1])
            tile_pixels.append(image[coords_to_index(coords, size[0])])
    return tile_pixels, tile_size


def apply_tile_to_image(image, size, tile, tile_size, tile_corner):
    """
    Copies a tile with a given offset onto an image
    :param image: The image the file is to be copied onto (as a list of (R,G,B) tuples)
    :param size: The size of the image as a tuple (width, height)
    :param tile: The tile to be copied over (as a list of (R,G,B) tuples)
    :param tile_size: The size of the tile as a tuple (width, height)
    :param tile_corner: The top left corner of the tile, in terms of the coordinates of the image, as a tuple (x,y)
    """
    for y in xrange(tile_size[1]):
        for x in xrange(tile_size[0]):
            img_coords = (x + tile_corner[0], y + tile_corner[1])
            image[coords_to_index(img_coords, size[0])] = tile[coords_to_index((x, y), tile_size[0])]


def sort_image_tiles(image, size, sorting_args, tile_size, tile_density=1.0, randomize_tiles=False):
    """
    Sorts an image by taking various tiles and sorting them individually.
    :param image: The image to be modified
    :param size: The size of the image, as (width, height)
    :param sorting_args: Arguments that would be passed to sort_pixels for each tile
    :param tile_size: The size of each tile as (width, height)
    :param tile_density: What fraction of the image is covered in tiles.
    :param randomize_tiles: Whether tiles should be distributed randomly
    :return: The modified image
    """
    out_image = list(image)
    width, height = size
    tile_width, tile_height = tile_size

    i = 0
    for y in xrange(0, height, tile_height):
        for x in xrange(0, width, tile_width):
            i += 1
            if randomize_tiles:
                # if using randomized tiles, skip a tile with probability 1 - density
                r = random()
                if r >= tile_density:
                    continue
            else:
                # if tiles are not randomized, add a tile once every 1/density times
                if tile_density == 0 or i < 1.0 / tile_density:
                    continue
                else:
                    i -= 1.0 / tile_density
            # extract a tile, sort it, and copy it back to the image
            tile, current_tile_size = get_tile_from_image(image, size, (x, y), tile_size)
            sorted_tile = sort_pixels(tile, current_tile_size, **sorting_args)
            apply_tile_to_image(out_image, size, sorted_tile, current_tile_size, (x, y))
    return out_image


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
    parser.add_argument("--use-tiles", action='store_true', default=False,
                        help="Whether to sort the image in tiles")
    parser.add_argument("--tile-x", type=int, default=100, help="The width of each tile, in pixels")
    parser.add_argument("--tile-y", type=int, default=100, help="The width of each tile, in pixels")
    parser.add_argument("--randomize-tiles", action='store_true', default=False,
                        help="Whether to distribute tiles randomly")
    parser.add_argument("--tile-density", type=float, default=1.0,
                        help="Approximately what fraction of the image is covered in tiles")

    args = parser.parse_args()

    # load image
    img = Image.open(args.infile)
    original_pixels = list(img.getdata())

    key = PIXEL_KEY_DICT.get(args.sortkey.lower(), None)

    path = PIXEL_PATH_DICT.get(args.path.lower(), None)

    sorting_args = {
        'randomize': args.randomize,
        'vertical': args.vertical,
        'path': path,
        'max_interval': args.interval,
        'progressive_amount': args.progressive_amount,
        'discretize': args.discretize,
        'reverse': args.reverse,
        'key': key,
    }

    tile_args = {
        'tile_size': (args.tile_x, args.tile_y),
        'randomize_tiles': args.randomize_tiles,
        'tile_density': args.tile_density,
    }

    if args.use_tiles:
        out_pixels = sort_image_tiles(original_pixels, img.size, sorting_args=sorting_args, **tile_args)
    else:
        out_pixels = sort_pixels(original_pixels, img.size, **sorting_args)

    # write output image
    img_out = Image.new(img.mode, img.size)
    img_out.putdata(out_pixels)
    img_out.save(args.outfile)


if __name__ == '__main__':
    main()
