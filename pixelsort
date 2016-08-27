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
import logging
import os
import re
from random import seed
from urllib.request import urlopen

from PIL import Image

from pixelsorter import images2gif
from pixelsorter.images2gif import get_gif_frames
from pixelsorter.paths import PIXEL_PATH_DICT
from pixelsorter.sort import sort_image_tiles, sort_image, splice_channel, SortingArgs

# get logger for current script (even across different modules)
logger = logging.getLogger(__name__)


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
