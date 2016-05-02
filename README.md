
# PixelSorting

A python library for pixel-sorting images.
This includes a script for easy pixel sorting from the command line, as well as
library code that is abstracted and easily extensible for custom features.

## Features
 - A variety of sorting paths
 - Many different sort functions
 - Edge detection for sorting boundaries
 - Sorting individual tiles within an image

## Installation
PixelSorting requires the Pillow module for image manipulation.

One can run ` pip install -r requirements.txt` to download any necessary modules.

## Usage

To run the script, use the command `python pixelsort.py <image> -o <result>` to sort a given image
and store it in `<result>`. The other settings and options are described below.
For the example figures, the original image used is this:

![Original Image][original]

#### Sorting Interval:

The `-i` or `--interval` argument specified the length of individual intervals of pixels to sort.
By default, whole rows of the image are sorted at once. However, when `-i <INTEGER>` is used,
pixels are sorted in consecutive groups of the given length.

With `-i` omitted:

![Default sorting interval][default]

With `-i 50`:

![Sorting interval of 50px][sort50]

With `-i 100`:

![Sorting interval of 100px][sort100]

The `-r` or `--randomize` argument will cause pixel intervals to have random length between 1 and `INTERVAL` pixels,
where `INTERVAL` is the amount specified by the `-i` flag. If the `-i` flag is omitted, then `-r` has no effect.

With `-i 50`:

![Uniform sorting interval of 50px][sort50]

With `-i 50 -r`:

![Random sorting interval of 50px][sort50random]

The `--progressive-amount <AMOUNT>` flag takes a floating point amount,
and increases the sorting interval by the given amount each row, as a fraction of the total interval.
For instance, with `-i 100` and `--progressive-amount 0.01`,
the sorting interval would increase by 1 pixel each row.
Since there are hundreds of rows in an image, values less than `0.001` usually work best.

With `-i 100 -r` and no progressive sorting:

![Sorting with random interval of 100][sort100random]

With `-i 100 -r --progressive-amount 0.0001`:

![Sorting with random interval of 100 and progressive sorting][sort100-progressive]

(It is difficult to see, but the sorting intervals near the top rows are smaller than at the bottom.)

#### Sorting Keys:

One can apply a custom function to pixels before they are sorted,
allowing one to sort by brightness, saturation, or some other metric.
This is done using the `-s <KEY>` or `--sortkey <KEY>` flag, where `<KEY>`
is one of a set of predefined function names.
By default, pixels are sorted simply using their numerical value.
Note that sorting is stable, so if pixels are mapped to the same value,
their relative position will be unchanged.

Default sorting method:

![Default sorting method][sort-default]

Using `-s sum` will sort by the sum of the pixel's (R,G,B) values:

![Sorting by pixel sum][sort-sum]

Using `-s red|green|blue` will sort using only the given channel of each pixel.
Sorting with `-s blue` is shown below.

![Sorting by pixel sum][sort-blue]

Other sorting methods include:
 - `chroma`
 - `hue`
 - `intensity`
 - `lightness`
 - `luma`
 - `saturation`
 - `value`

Using the `-R` or `--reverse` flag will reverse the sorting order of the pixels:

With `-i 50`:

![Uniform sorting interval of 50px][sort50]

With `-i 50 -R`:

![Reversed sorting interval of 50px][sort50reverse]

The `-d` or `--discretize <INTEGER>` flag will take pixel values,
divide them by the given amount, and cast to an integer.
This means that pixels with small variations will be binned into the same categories,
and not sorted relative to each other.
This allows one, for instance, to only move the "brightest" pixels while the other pixels stay in place.

With `-s sum` and `-d` omitted:

![Sorting by sum][sort-sum]

With `-s sum -d 100`:

![Sorting by sum with -d 100][sort-sum-d100]

With `-s sum -d 200`:

![Sorting by sum with -d 200][sort-sum-d200]

#### Sorting Paths

By default, all sorting is done in horizontal intervals through the image.
However, several other sorting paths are available.

The `-v` flag will sort the image vertically instead of horizontally.
Otherwise, one can explicitly specify what type of path to use with the `-p` or `--path` flag:
 - `concentric` Instead of rows, sorts concentric rectangles around the image.

![Sorting with concentric path][sort100-concentric]

 - `diagonal` Sorts in diagonal lines that move from the top left to the bottom right.

![Sorting with diagonal path][sort100-diagonal]

 - `diagonal-single` Similar to `diagonal`, but all the diagonal lines are connected in one huge path.
  Good for creating really smooth gradients.

![Sorting with diagonal-single path][sort-diagonal-single]

 - `horizontal`: The default, sorts horizontally row by row

![Sorting with horizontal path][sort100random]

 - `random-walk`: Starting on the left, performs a random walk to the right side of the image,
 randomly moving up or down one pixel at a time

![Sorting with random walk path][sort100-random-walk]

 - `vertical`: Sorts vertically, column by column

![Sorting with concentric path][sort100-vertical]

#### Edge Detection

Edge detection allows one to break up sorting intervals are points of high contrast
(i.e. where there are edges in the image). This creates the effect of only sorting within low-contrast regions.
The `-e <THRESHOLD>` or `--edge-threshold <THRESHOLD>` flag can be used to specify a numerical threshold above
pixels are considered "edges". Intuitively, this means that low thresholds will cause images with very short sorting
intervals, while very high threholds will cause the image to be almost completely sorted, as if `-e` had
not been specified at all. However, the exact effects depend on the image specified.

The original image:

![Original Image][original]

Sorting with `-e 50`:

![Sorting with -e 50][sort-edge-detect-50]

Sorting with `-e 100`:

![Sorting with -e 100][sort-edge-detect-100]

Sorting with `-e 200`:

![Sorting with -e 200][sort-edge-detect-200]

Sorting without the `-e` flag:

![Sorting without -e][default]

a

[//]: # "Figures"
[original]: docs/figures/original.jpg
[default]: docs/figures/sort-sum.jpg
[sort50]: docs/figures/sort-50.jpg
[sort100]: docs/figures/sort-100.jpg
[sort50random]: docs/figures/sort-50-random.jpg
[sort100random]: docs/figures/sort-100-random.jpg
[sort-default]: docs/figures/sort-default.jpg
[sort-sum]: docs/figures/sort-sum.jpg
[sort-blue]: docs/figures/sort-blue.jpg
[sort50reverse]: docs/figures/sort-50-reverse.jpg
[sort-sum-d100]: docs/figures/sort-sum-d100.jpg
[sort-sum-d200]: docs/figures/sort-sum-d200.jpg
[sort100-progressive]: docs/figures/sort-100-progressive.jpg
[sort100-concentric]: docs/figures/sort-100-concentric.jpg
[sort100-diagonal]: docs/figures/sort-100-diagonal.jpg
[sort-diagonal-single]: docs/figures/sort-diagonal-single.jpg
[sort100-random-walk]: docs/figures/sort-100-random-walk.jpg
[sort100-vertical]: docs/figures/sort-100-vertical.jpg
[sort-edge-detect-50]: docs/figures/sort-edge-detect-50.jpg
[sort-edge-detect-100]: docs/figures/sort-edge-detect-100.jpg
[sort-edge-detect-200]: docs/figures/sort-edge-detect-200.jpg
