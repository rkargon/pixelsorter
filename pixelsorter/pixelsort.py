#!/usr/bin/env python3

#  This file is part of Pixelsorting.
#
# Pixelsorting is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pixelsorting is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pixelsorting.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import collections
import logging
import os
import re
from math import ceil
from random import randint, random, seed, randrange
from urllib.request import urlopen

from PIL import Image

from pixelsorter import images2gif
from pixelsorter.edge_detection import edge_detect
from pixelsorter.pixelkeys import PIXEL_KEY_DICT, luma
from pixelsorter.pixelpaths import PIXEL_PATH_DICT
from pixelsorter.pixelpaths import horizontal_path
from pixelsorter.pixelpaths import vertical_path
from pixelsorter.util import clamp
from pixelsorter.util import coords_to_index

# get logger for current script (even across different modules)
logger = logging.getLogger(__name__)


class SortingArgs(collections.MutableMapping):
    """
    A class for storing sorting options. It inherits from collections.MutableMapping so that options can be
    accessed and modified using the [] operator. It can also be passed as **kwargs into a function.
    For accessing path arguments, one can use the prefix ".path", e.g. sort_args["path.angle"].
    """

    def __init__(self, cli_args, size):
        """
        Sets up sorting arguments from the given command line arguments
        :param cli_args: The command line arguments returned from argparse
        :param size: The size of the image
        """
        image_mask = None
        if cli_args.image_mask is not None:
            mask_img = Image.open(cli_args.image_mask)
            if mask_img.size != size:
                print("Error: Image mask is not the same size as input image.")
                exit()
            image_mask = list(mask_img.getdata())
        key = PIXEL_KEY_DICT.get(cli_args.sortkey.lower(), None)

        # parse pixel path, and any arguments given
        path_name, path_kwargs = cli_args.path
        if path_name is None:
            path = None
        else:
            path = PIXEL_PATH_DICT.get(path_name, None)

        self.discretize = cli_args.discretize
        self.edge_threshold = cli_args.edge_threshold
        self.edge_data = None
        self.key = key
        self.image_threshold = cli_args.image_threshold
        self.image_mask = image_mask
        self.max_interval = cli_args.max_interval
        self.path = path
        self.path_kwargs = path_kwargs
        self.progressive_amount = cli_args.progressive_amount
        self.randomize = cli_args.randomize
        self.reverse = cli_args.reverse
        self.vertical = cli_args.vertical
        # path splicing settings
        self.mirror = cli_args.mirror
        self.splice = cli_args.splice
        self.splice_random = cli_args.splice_random

    def __len__(self):
        return len(self.__dict__)

    def __iter__(self):
        yield from self.__dict__.keys()

    def __getitem__(self, key):
        if hasattr(self, key):
            return self.__getattribute__(key)
        elif key.startswith("path."):
            path_arg = key[len("path."):]
            return self.path_kwargs[path_arg]
        else:
            raise KeyError("No parameter %s in sort settings." % key)

    def __delitem__(self, key):
        pass

    def __setitem__(self, key, value):
        if hasattr(self, key):
            self.__setattr__(key, value)
        elif key.startswith("path."):
            path_arg = key[len("path."):]
            self.path_kwargs[path_arg] = value
        else:
            raise KeyError("No parameter %s in sort settings." % key)


def sort_image(image, size, vertical=False, path=None, path_kwargs=None, max_interval=0, progressive_amount=0,
               randomize=False,
               edge_threshold=0, edge_data=None, image_threshold=None, image_mask=None, key=None, discretize=0,
               reverse=False,
               mirror=False, splice=0, splice_random=False):
    """
    Applies pixel sorting to an image. This is done by first creating a sort mask that describes the sorting intervals,
    and then calling apply_sort_mask to the image using the generated mask.
    :param discretize: Amount by which to "discretize" pixel values. This is done by dividing each pixel's value
    (after applying the sort key) by the given amount and then converting to an integer.
    This would mean that pixels are "binned" into discrete categories, and sorting would be different.
    Since sorting is stable, this means that pixels with low-level noise remain grouped together,
    and small details can be preserved in sorting.
    :param progressive_amount: If this is non-zero,
    then the sorting interval increases as one progresses row-by-row through the image.
    progressive_amount indicates the amount, in pixels, by which to increase the sorting interval after each row.
    :param path: The specific path used to iterate through the image, as a list of rows,
    where each row is a list of (x, y) coordinates.
    :param path_kwargs: Arguments that should be passed to the path iterator.
    :param image: A list of tuples (R,G,B) representing the pixels of the image
    :param size: The size of the image as a tuple (width, height)
    :param vertical: Whether or not the color sorting is applied vertically (the default is horizontal)
    :param max_interval: The largest interval of adjacent pixels to sort
    :param randomize: Whether to use random intervals of pixels
    :param key: The function to use for sorting, e.g. brightness or red amount.
                This function takes a pixel and returns a value to be sorted.
    :param reverse: Whether or not to reverse the direction of the sorting
    :param mirror: Mirrors each pixel interval after sorting.
    :param splice: Splices each pixel interval after sorting, at the given position (from 0.0 to 1.0).
    :param splice_random: Splices each pixel interval at a random position.
    :param edge_threshold: If greater than zero, stops sorting intervals at pixels whose "edge detection" value
    is greater than the given threshold.
    :param edge_data: Stores edge data for the image, if it is already cached.
    :param image_threshold: If not None, uses pixel's brightness to determine sort intervals.
    Pixels that are outside the range [threshold, MAX - threshold] are not sorted. So a value of 0 will sort all pixels
    (depending on the value of other arguments, of course), while a value of 1 will not sort any pixels.
    :param image_mask: The image to use as an initial sorting mask. Edge data and other sorting intervals
    will be applied on top of this.
    :return: The pixels of the resulting image as a list of (R,G,B) tuples
    """
    width, height = size
    out_pixels = list(image)

    # get edge data if necessary
    if edge_threshold > 0 and edge_data is None:
        edge_data = edge_detect(image, size)

    if image_threshold is not None:
        image_threshold = clamp(image_threshold, 0.0, 1.0)

    if discretize > 0 and key is not None:
        def sort_key(p):
            return int(key(p) / discretize)
    else:
        sort_key = key

    # if path not given, use a horizontal or vertical path
    if path is None:
        if vertical:
            path_iterator = vertical_path(size)
        else:
            path_iterator = horizontal_path(size)
    else:
        # path_iterator = path_generator(size, **(path_kwargs if path_kwargs is not None else {}))
        path_iterator = path(size, **path_kwargs)

    # check if interval should increase progressively through image
    if progressive_amount > 0:
        current_max_interval = max_interval * progressive_amount
    else:
        current_max_interval = max_interval

    # traverse image and compute random sort intervals
    pixels_sorted = 0
    for row_iter in path_iterator:
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
            i = 0

            px_indices = []
            # if interval is 0, just sort whole line at once
            while i < interval or interval == 0:
                try:
                    coords = next(row_iter)
                except StopIteration:
                    path_finished = True
                    break

                i += 1
                pixels_sorted += 1
                if pixels_sorted % 200000 == 0:
                    logger.info("Created sort mask for %d / %d pixels (%2.2f%%)..." %
                                (pixels_sorted, width * height, 100 * pixels_sorted / float(width * height)))

                idx = coords_to_index(coords, width)

                # use various image data to set up sort intervals, before computing random intervals
                if image_mask is not None and luma(image_mask[idx]) > 128:
                    break
                # edge detection
                if edge_data is not None and edge_data[idx] > edge_threshold > 0:
                    break
                # use image color to determine ends of sorting intervals
                if image_threshold is not None:
                    brightness = luma(image[idx])
                    t = image_threshold * 255 / 2
                    if brightness < t or brightness > 255 - t:
                        break

                # add current pixel to interval
                px_indices.append(idx)

            # sort pixels, apply to output image
            if len(px_indices) > 0:
                sorted_pixels = sorted([out_pixels[i] for i in px_indices], key=sort_key, reverse=reverse)
                sorted_pixels = sort_filter(sorted_pixels, mirror=mirror, splice=splice, splice_random=splice_random)
                for i in range(len(px_indices)):
                    index = px_indices[i]
                    pixel = sorted_pixels[i]
                    out_pixels[index] = pixel

    return out_pixels


def sort_filter(l, mirror=False, splice=0, splice_random=False):
    """
    Rearranges an interval of pixels.
    :param l: The interval, as a list of pixels
    :param mirror: Whether to put each element in the list alternatively at the start or end of the list, effectively
    mirroring a sorted list.
    This is particularly useful with pixel paths that are looped, so that the beginning and end will not be
    discontinuous.
    :param splice: A value in the range [0,1] that picks a point in the list and makes it the start of the interval
    pixels before this element are moved to the end. A value of 0 uses the existing first element of the list as the
    starting point, and a value of 1 makes the last element in the list be the start.
    :param splice_random: Splices the list at a random point.
    :return: A modified copy of the list of pixels.
    """
    # TODO documentation
    if len(l) == 0:
        return l
    nl = list(l)

    if mirror:
        get_index = put_index = 0
        while get_index < len(l):
            nl[put_index] = l[get_index]
            get_index += 1
            if put_index >= 0:
                put_index += 1
            put_index *= -1

    if splice_random:
        splice_start = randrange(len(l))
    elif splice > 0:
        splice_start = int((len(l) - 1) * splice)
    else:
        splice_start = None

    if splice_start is not None:
        nl = nl[splice_start:] + nl[:splice_start]

    return nl


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
    for y in range(tile_size[1]):
        for x in range(tile_size[0]):
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
    for y in range(tile_size[1]):
        for x in range(tile_size[0]):
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
    total_tiles = ceil(height / float(tile_height)) * ceil(width / float(tile_width))
    tiles_completed = 0
    pixels_per_tiles = tile_width * tile_height
    for y in range(0, height, tile_height):
        for x in range(0, width, tile_width):
            # logging
            tiles_completed += 1
            if tiles_completed % (200000 / pixels_per_tiles) == 0:
                logger.info("Completed %d / %d tiles... (%2.2f%%)" %
                            (tiles_completed, total_tiles, 100.0 * tiles_completed / total_tiles))

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
            sorted_tile = sort_image(tile, current_tile_size, **sorting_args)
            apply_tile_to_image(out_image, size, sorted_tile, current_tile_size, (x, y))

    return out_image


def splice_channel(original, sorted_img, channel):
    if len(original) != len(sorted_img):
        raise ValueError("Input images are not the same size.")
    channels = ["red", "green", "blue"]
    if channel not in channels:
        raise ValueError("Invalid channel")
    channel_idx = channels.index(channel)

    out_pixels = list(original)
    for i in range(len(out_pixels)):
        p = list(out_pixels[i])
        p[channel_idx] = sorted_img[i][channel_idx]
        out_pixels[i] = tuple(p)
    return out_pixels


def sort_image_with_cli_args(image, outfile, sorting_args, tile_args=None, channel=None, pixels=None, save=None):
    """
    Sorts an image with the given command line parameters, and outputs the result to the given file.
    :param outfile: The name of the file to write to
    :param image: The image to sort, as a PIL.Image object
    :param sorting_args: Arguments for sorting
    :param tile_args: Arguments for tiles
    :param channel: The specific channel (if None, sorts all channels) to sort
    :param pixels: The pixel data of the image, as a list of (R,G,B) tuples.
    :param save: Whether or not to save the sorted image to a file.
    By default this is None, but this can be specified so one does not need to re-load the image data every time.
    (For instance, if this is called repeatedly while creating an animation)
    :return: The resulting image object
    """
    if pixels is None:
        pixels = list(image.getdata())
    if tile_args is not None:
        out_pixels = sort_image_tiles(pixels, image.size, sorting_args=sorting_args, **tile_args)
    else:
        out_pixels = sort_image(pixels, image.size, **sorting_args)

    if channel is not None:
        out_pixels = splice_channel(pixels, out_pixels, channel)

    # write output image
    img_out = Image.new(image.mode, image.size)
    img_out.putdata(out_pixels)
    if save:
        img_out.save(outfile)
    logger.info("Wrote image to %s." % outfile)

    return img_out


def parse_path_args(arg_str):
    """
    parse pixel path, and any arguments given
    :param arg_str: The string of path arguments, in the form "path_name arg1=val1 arg2=val2 ..."
    :return: The name of the path, and a dict holding the path arguments.
    """
    path_split = arg_str.lower().split()
    if len(path_split) == 0:
        return None, None
    else:
        path_name, *path_args = path_split
        path = PIXEL_PATH_DICT.get(path_name, None)

        path_args = [parse_single_path_arg(a) for a in path_args]
        if None in path_args:
            print("Error: Arguments for path must be all of type 'name=value'.")
            exit()
        path_kwargs = dict(path_args)
        # some janky reflection to get the number of arguments that this type of path accepts
        arg_count = path.__code__.co_argcount - 1
        if arg_count < len(path_kwargs):
            print("Error: Path '%s' only takes %d argument(s)." % (path_name, arg_count))
            exit()
        return path_name, path_kwargs


def parse_single_path_arg(arg):
    """
    Parses a single path argument
    :param arg: The argument in the form "arg_name=value"
    :return: A tuple (arg_name, value)
    """
    m = re.match(r"^([^=]+?)=([^=]+?)$", arg)
    if m is None:
        return None
    else:
        arg_name, arg_value = m.groups()
        return arg_name, parse_arg_type(arg_value)


def parse_arg_type(arg):
    """
    Parses the type of an argument based on its string value.
    Only checks ints, floats, and bools, defaults to string.
     For instance, "4.0" will convert to a float(4.0)
    :param arg: The argument value
    :return: The value converted to the proper type.
    """
    if type(arg) != str:
        return arg
    else:
        # check int
        try:
            return int(arg)
        except ValueError:
            pass
        # check float
        try:
            return float(arg)
        except ValueError:
            pass
        # check bool
        if arg.lower() == "true":
            return True
        elif arg.lower() == "false":
            return False
        # return any other string
        return arg


def str_to_animate_params(s):
    """
    Parses animation parameters
    :param s: A string of the form "<param> <start> <stop> <n_steps>"
    :return: A tuple containing each field, (param: str, start: float, stop: float, n_steps: int)
    """
    param, start, stop, n_steps = s.split(" ")
    return param, float(start), float(stop), int(n_steps)


def get_gif_frames(img):
    """
    Extracts the frames from an animated gif.
    :param img: A PIL Image object
    :return: An array of PIL image objects, each corresponding to a frame in the animation.
    """
    gif_frames = []
    n = 0
    while img:
        if img.mode != "RGB":
            image = img.convert(mode="RGB")
        else:
            image = img
        gif_frames.append(image)
        n += 1
        try:
            img.seek(n)
        except EOFError:
            break
    return gif_frames


def get_cli_args():
    """
    Parses command line arguments.
    :return: An object whose fields are the command line arguments.
    """
    parser = argparse.ArgumentParser(description='A tool for pixel-sorting images')
    parser.add_argument("infile", help="The input image")
    parser.add_argument("-o", "--outfile", required=True, help="The output image")
    parser.add_argument("--log", action="store_true", default=False, help="Prints out progress and other messages.")
    parser.add_argument("--channel", type=str, default=None, choices=["red", "green", "blue"],
                        help="Sort only one of the channels of this image.")
    parser.add_argument("-d", "--discretize", type=int, default=0,
                        help="Divides float values of pixels by the given integer amount, and casts to an int. "
                             "Used to bin pixel values into several discrete categories.")
    parser.add_argument("-e", "--edge-threshold", type=float, default=0,
                        help="Uses edge detection to limit sorting intevals between pixels "
                             "who exceed the given contrast threshold.")
    parser.add_argument("--image-threshold", type=float, default=None)
    parser.add_argument("--image-mask", type=str, default=None, help="Use a custom image for generating the mask")
    parser.add_argument("-i", "--max-interval", type=int, default=0,
                        help="The size of each sorting interval, in pixels. If 0, whole row is sorted. "
                             "If intervals are randomized, then this is the maximum size of the inerval.")
    parser.add_argument("-m", "--mirror", action='store_true', default=False,
                        help="Make sorted intervals symmetric from start to end.")
    parser.add_argument("-p", "--path", type=parse_path_args, default="",
                        help="The type of path used to sort over the image. Horizontal by default.")
    parser.add_argument("--help-paths", action='store_true', default=False, help="Display info about sorting paths.")
    parser.add_argument("--progressive-amount", type=float, default=0,
                        help="How fast interval size should increase as one moves through the image. "
                             "This is a ratio of the max interval size.")
    parser.add_argument("-r", "--randomize", action='store_true', default=False,
                        help="Whether to randomize pixel-sorting intervals")
    parser.add_argument("-R", "--reverse", action='store_true', default=False,
                        help="Whether to reverse pixel-sorting order")
    parser.add_argument("-s", "--sortkey", type=str, default="", help="Function applied to pixels to sort them.")
    parser.add_argument("-S", "--splice", type=float, default=0.0,
                        help="For each sort interval, takes part of the beginning of the interval and moves it to the "
                             "end. A value of 0 means no splicing is done, and 1 means the all elements up to the "
                             "last are moved.")
    parser.add_argument("--splice-random", action='store_true', default=False,
                        help="Randomly chooses splice point. (See \"--splice\".)")
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
    parser.add_argument("--animate", type=str_to_animate_params, default=None,
                        help="Animate a certain parameter. "
                             "This argument is a string '<param> <start> <stop> <n_steps>'")
    parser.add_argument("--save-frames", action='store_true', default=False,
                        help="Whether to save animation frames as individual pictures")
    parser.add_argument("--fix-random-seed", action='store_true', default=False,
                        help="Set the random seed to 0 at the start of the program. Useful for testing and debugging.")
    args = parser.parse_args()
    return args


def print_paths_help():
    print("Sorting paths specify in which direction pixels are sorted in the image.\n"
          "By default, the path is 'horizontal'.\n"
          "The syntax for specifying sort paths is: '<path-name> [arg1=val1, arg2=val2, ...]'.\n"
          "For detailed documentation on sort paths, see docs/PATHS.md.\n\n"
          "The available path names are:")
    print(" - angled-line [angle=float]:    Sort pixels in lines tilted at the given angle.")
    print(" - circles:                      Pixels are sorted in concentric circles about the center of the image.")
    print(" - concentric:                   Pixels are sorted in concentric rectangles.")
    print(" - diagonal:                     Pixels are sorted in diagonal lines.")
    print(" - diagonal-single:              Pixels sorted in a single path that moves diagonally through the image.")
    print(" - fill-circles [radius=int]:    Covers the image in circles of the given radius")
    print(" - horizontal:                   Pixels sorted horizontally.")
    print(" - random-walk:                  Pixels sorted in random walks over the image.")
    print(" - random-walk-horizontal:       Pixels sorted in random walks moving horizontally over the image. ")
    print(" - random-walk-vertical          Pixels sorted in random walks moving vertically over the image. ")
    print(" - vertical:                     Pixels sorted vertically.")


def main():
    args = get_cli_args()

    # print detailed help if necessary
    if args.help_paths:
        print_paths_help()
        return

    # set up logging
    if args.log:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    # fix random seed if necessary
    if args.fix_random_seed:
        seed(0)

    # load image
    logger.info("Loading image...")
    if re.match(r"https?://", args.infile):
        response = urlopen(args.infile)
        img_size = int(response.getheader("Content-Length"))
        logger.info("Downloading file (%dKB)..." % (img_size // 1000))
        img = Image.open(response)
    else:
        img = Image.open(args.infile)
    gif = None
    if img.tile[0][0] == "gif":
        gif = True
    # converting modes in gifs seems to remove all frames but the first
    if img.mode != "RGB" and not gif:
        img = img.convert(mode="RGB")

    # set up sorting args object
    sorting_args = SortingArgs(cli_args=args, size=img.size)

    # tile args
    use_tiles = args.use_tiles
    if use_tiles:
        tile_args = {
            'tile_size': (args.tile_x, args.tile_y),
            'randomize_tiles': args.randomize_tiles,
            'tile_density': args.tile_density,
        }
    else:
        tile_args = None

    if args.animate is None:
        if gif:
            gif_frames = []
            frames = get_gif_frames(img)
            for f in frames:
                frame = sort_image_with_cli_args(image=f, outfile=args.outfile, sorting_args=sorting_args,
                                                 tile_args=tile_args, channel=args.channel, pixels=None,
                                                 save=args.save_frames)
                gif_frames.append(frame)
            images2gif.writeGif(args.outfile, gif_frames, subRectangles=False)
        else:
            logger.info("Sorting image....")
            sort_image_with_cli_args(image=img, outfile=args.outfile, sorting_args=sorting_args, tile_args=tile_args,
                                     channel=args.channel, pixels=None, save=True)
    else:
        # set up animation params
        param, start, stop, n_steps = args.animate
        sorting_args[param] = start

        gif_frames = []
        # create directory to hold temporary frames
        dir_path = ""
        if args.save_frames:
            dir_path = args.outfile + "_frames/"
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

        if gif:
            frames = get_gif_frames(img)
            n_steps = len(frames)
        else:
            frames = None

        delta = (stop - start) / max(1, n_steps - 1)
        n_digits = len(str(n_steps))
        format_str = "%%s%%s_frame_%%0%dd.png" % n_digits
        for i in range(n_steps):
            logger.info("sorting %s = %f..." % (param, sorting_args[param]))
            frame_name = format_str % (dir_path, args.outfile, i)
            f = frames[i] if gif else img
            out_pixels = sort_image_with_cli_args(f, frame_name, sorting_args, tile_args, channel=args.channel,
                                                  pixels=f.getdata(), save=args.save_frames)
            gif_frames.append(out_pixels)
            sorting_args[param] += delta
            i += 1

        images2gif.writeGif(args.outfile, gif_frames, subRectangles=False)


if __name__ == '__main__':
    main()
