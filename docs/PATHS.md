# PixelSorting – Sort Paths

Sorting paths specify the directions in which pixels are sorted on an image. For example,
by default the sort path is horizontal, so pixels are sorted row-by-row.
Consecutive rows move down vertically through the image.

Every path is defined in this way - as a series of "rows" (or intervals), in which each row is a set of pixels.
Ideally, each pixel in a "row" would be close to the previous pixel, and each row would be close to the previous one.
Thus, a sorting path can "sweep over" the area of the image and cover it completely.
In a way, a sort path corresponds to a two-dimensional *parametrization* of the image plane.

However, sort paths don't have to be constrained in this way, and can pretty much be arbitrary sets of sets of pixels.

One can specify the type of sort path using the command line argument `-p|--path <pathname>`.
Some paths accept arguments, which can be specified using the syntax:
`-p|--path "<pathname> <arg1>=<val1> <arg2>=<val2> ..."`.

## Built-in Paths
The pixelsorting script has the following built-in sorting path options:
- `angled-line`
- `circles`
- `concentric`
- `diagonal`
- `diagonal-single`
- `fill-circles`
- `horizontal`
- `random-walk`
- `random-walk-horizontal`
- `random-walk-vertical`
- `vertical`

#### angled-line

The angled-line path consists of a series of adjacent rows of pixels,
where each row is a series of pixels in a line, at a certain angle.

**Parameters**:
 - `angle` --- The angle of the lines in degrees. By default, this is `0`.

The following image shows this sort path with an angle of 60 degrees:

![sort with 60° angle][angled-line-60]

#### circles

The circles path consists of a series of concentric circles.
The circles expand until every part of the image, including the corners, is covered.

The following image shows this sort path:

![sort with concentric circles][circles]


#### concentric

The concentric path consists of a series of concentric rectangles, starting with the border of the image and moving inwards.

![sort with concentric rectangles][concentric]

#### diagonal

The diagonal path consists of a series of diagonal lines moving from the top left to the bottom right of the image.
Successive lines start at the bottom-left corner and move up until the top-right corner.

![sort with diagonal lines][diagonal]

#### diagonal-single

This is similar to the diagonal path, except that instead of a series of consecutive lines, all the paths are combined into a single line.
This creates a very smooth progression moving diagonally through the image.

![sort with diagonal-single path][diagonal-single]

#### fill-circles

This path covers an image with a series of overlapping circles. Each circle is like the `circles` path,
in that it contains concentric rings of pixels forming a circle.

**Parameters**
 - `radius` --- The radius of each individual circle. By default, this is `100`.

 The following image shows this sort path with a radius of 30:

![sort with fill-circles path][fill-circles-30]

#### horizontal

This is the default sort path. It sorts pixels in horizontal rows,
with each row one pixel below the previous one.

![sort with horizontal lines][horizontal]

#### random-walk

Sorts pixels in a series of random walks over the image.
The random walks terminate when they reach the edge of the image.
The number of random walks is such that, roughly,
the number of pixels covered in the walks is equal
to the total number of pixels in the image.
However, since walks often overlap, the whole image is rarely covered.

![sort with random walk][random-walk]

#### random-walk-horizontal

This sorts pixels in a series of horizontal random walks.
For each row of the image, a line starts on the left-most pixel, and then moves to the right,
randomly shifting up or down a pixel each step.

![sort with horizontal random walk][random-walk-horizontal]

#### random-walk-vertical

This sorts pixels in a series of vertical random walks.
For each column of the image, a line starts on the top pixel, and then moves down,
randomly shifting left or right a pixel each step.

![sort with vertical random walk][random-walk-vertical]

#### vertical

Similar to the horizontal path, this sorts an image in a series of vertical lines moving across the image.

![sort with vertical lines][vertical]

## Custom paths

While it is not possible to specify custom paths from the command line,
they can be created programmatically and passed to the sorting function in a Python script.
Each sort path is simply a generator of generators of pixels.
This means that each sort path is a function that, when called,
yields a series of "intervals", and each interval yields a series of `(x,y)` tuples representing pixel
coordinates.
The function should accept a tuple of (width, height) which represents the dimensions of the image.

For example, here is an implementation of the `horizontal` sort path:

```python
def horizontal_path(size):
    width, height = size
    return (((x, y) for x in range(width)) for y in range(height))
```

Then, sort paths are called in the following fashion:

```python
pixel_iterator = your_sort_path(img_size)
for row in pixel_iterator:
    for pixel in row:
        x, y = pixel
        # do stuff with pixel....
```

[//]: # "Figures"
[angled-line-60]: figures/sort-angled-line-60.jpg
[circles]: figures/sort-circles.jpg
[concentric]: figures/sort-100-concentric.jpg
[diagonal]: figures/sort-100-diagonal.jpg
[diagonal-single]: figures/sort-diagonal-single.jpg
[fill-circles-30]: figures/sort-fill-circles-30.jpg
[horizontal]: figures/sort-100-random.jpg
[random-walk]: figures/sort-100-random-walk.jpg
[random-walk-horizontal]: figures/sort-100-random-walk-horizontal.jpg
[random-walk-vertical]: figures/sort-100-random-walk-vertical.jpg
[vertical]: figures/sort-100-vertical.jpg
