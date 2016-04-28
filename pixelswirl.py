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

def tiled_path(size, max_x, max_y):
    """
    Creates a generator for progressing vertically through an image.
    :param size: A tuple (width, height) of the image size
    :return: A generator that yields a set of columns through the image.
    Each column is a generator that yields pixel coordinates.
    """
    width, height = size

    def tile_path_iter(x, y, max_x, max_y):
        last = [0, 0]
        for i in range(max(max_x, max_y)*4*max(max_x,max_y)):
            if last[0] < max_x and last[1] < max_y:
                actual = (last[0]+x, last[1]+y)
                yield actual
            if last[1] == 0:
                last[1] = last[0] + 1
                last[0] = 0
            else:
                last[1] -= 1
                last[0] += 1 

    for x in range(0, width-max_x,max_x):
        for y in range(0, height-max_y, max_y):
            yield tile_path_iter(x, y, max_x, max_y)

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


def sort_pixels(pixels, size, iterator=horizontal_path, max_x=50, max_y=50, max_interval=100, chance=1.0,  randomize=False, key=None, reverse=False):
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
    pixel_iterator = iterator(size, max_x, max_y)
    #pixel_iterator = concentric_rectangle_path(size)

    # for each path
    for path in pixel_iterator:
        path_finished = False
        # traverse path until it is finished
        if random() > chance:
            continue
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

def sort_pixel_tiles(pixels, size, max_x=50, max_y=50, tile_num=25, randomize=False, key_x=None, key_y=None):
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

    out_pixels = create_2D_list(out_pixels, width)

    if randomize:
        sampling = [(randint(0, width-max_x),randint(0, height-max_y)) for i in range(tile_num)]
    else:
        sampling = [((i*max_x*2) % (width-max_x),((((i*max_x*2) / (width-max_x))*max_y) % (height-max_y))) for i in range(tile_num)]


    for (x, y) in sampling:
        print x, y
        rows = []
        for row in range(max_y):
            unsorted_pixels = out_pixels[y+row][x:x+max_x]
            sorted_pixels = sorted(unsorted_pixels, key=key_x)
            rows.append(sorted_pixels)
        sorted_rows = sorted(rows, key=lambda row: key_y([sum([p[i] for p in row])/float(len(row)) for i in range(3)])) #efrodizzyak
        for iy in range(max_y):
            for ix in range(max_x):
                out_pixels[y+iy][x+ix] = sorted_rows[iy][ix]

    out_pixels = create_1D_list(out_pixels)
    return out_pixels

def create_2D_list(plist, width):
    return [[p for p in plist[y*width:(y+1)*width]] for y in range(len(plist)/width)]

def create_1D_list(plist):
    l = []
    for row in plist:
        for p in row:
            l.append(p)
    return l


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

    out_pixels = sort_pixels(original_pixels, img.size, randomize=False, iterator=tiled_path, max_x=60, max_y=240, max_interval=100000000, chance=0.2, key=(lambda x: sum(x)))

    out_pixels = sort_pixels(out_pixels, img.size, randomize=False, iterator=tiled_path, max_x=240, max_y=60, max_interval=100000000, chance=0.2, key=(lambda x: sum(x)))

    #out_pixels = sort_pixel_tiles(original_pixels, img.size, max_x=200, max_y=200, tile_num=13, randomize=False, key_x=lambda x: x[0] + x[1] + x[2], key_y=lambda y: y[2])

    # write output image
    img_out = Image.new(img.mode, img.size)
    img_out.putdata(out_pixels)
    img_out.save(outfile)


if __name__ == '__main__':
    main()
