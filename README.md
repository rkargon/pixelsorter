
# PixelSorting

A python library for pixel-sorting images.
This includes a script for easy pixel sorting from the command line, as well as
library code that is abstracted and easily extensible for custom features.

## Features
 - A variety of sorting paths
 - Many different sort functions
 - Edge detection for sorting boundaries
 - Sorting individual tiles within an image
 - Support for sorting GIFs and creating animated sorts.

## Installation
PixelSorting requires the Pillow module for image manipulation.

One can run ` pip install -r requirements.txt` to download any necessary modules.

## Usage

To run the script, use the command `python pixelsort.py <image> -o <result>` to sort a given image
and store it in `<result>`. Use the `--log` flag to view progress for sorting particularly large images.
Various sorting options are described in detail in [the full documentation](docs/DOCUMENTATION.md).
One can also run the script with the `-h|--help` flag to see the full list of options.

Given the following original image:

![Original Image][original]

The default sorting settings will produce:

![Default sorting][default]

One can also sort certain intervals using the `-i` flag.
The flags `-i 50 -r` will sort random intervals of length up to 50 pixels:

![Sorting random intervals][sort50random]

There are a variety of possible sorting paths, specified using the `-p` flag.
For example, `-i 100 -r -p diagonal` will produce:

![Sorting diagonally][sort100-diagonal]

Paths can also accept arguments.
For instance, the flag `-p "angled-line angle=60"` passes the argument `angle=60` to the `angled-line` path,
and sorts pixels in lines tilted at 60 degrees:

![Sorting with angled lines][sort-angled-line-60]

Sorting paths are explained in more detail in [the paths documentation](docs/PATHS.md).

### Animation

The pixelsorting script supports animation using the `--animate` flag.
The syntax is `--animate "<param> initial_value end_value num_frames"`,
where the given parameter is interpolated between the start and end values for the given number of frames.

For instance, the flags `--animate "max_interval 2 30 15` will produce the following animation:
![Animated sort][sort-animated]

One can also animate path arguments using the syntax `path.arg`.
For instance, `-p angled-line --animate "path.angle 0 90 20"` will produce a 20-frame animation
in which the angle of sorting goes from horizontal to vertical.

One can also run the script using animated GIFs as input.

[//]: # "Figures"
[original]: docs/figures/original.jpg
[default]: docs/figures/sort-sum.jpg
[sort50random]: docs/figures/sort-50-random.jpg
[sort100-diagonal]: docs/figures/sort-100-diagonal.jpg
[sort-angled-line-60]: docs/figures/sort-angled-line-60.jpg
[sort-animated]: docs/figures/sort-animated.gif
