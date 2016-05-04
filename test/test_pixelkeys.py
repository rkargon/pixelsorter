#!/usr/bin/python

import unittest

import pixelkeys


class TestPixelKeys(unittest.TestCase):
    def test_red(self):
        out = pixelkeys.red((1, 2, 3))
        self.assertEqual(out, 1)

    def test_green(self):
        out = pixelkeys.green((1, 2, 3))
        self.assertEqual(out, 2)

    def test_blue(self):
        out = pixelkeys.blue((1, 2, 3))
        self.assertEqual(out, 3)

    def test_intensity(self):
        out = pixelkeys.intensity((1, 2, 3))
        self.assertEqual(out, 2.0)

    def test_lightness(self):
        out = pixelkeys.lightness((1, 2, 11))
        self.assertEqual(out, 6.0)

    def test_luma(self):
        blue_out = pixelkeys.luma((10, 20, 30))
        self.assertEqual(blue_out, 18.596)
        # intuitively, equal amounts of green are brighter than blue.
        green_out = pixelkeys.luma((20, 30, 10))
        self.assertGreater(green_out, blue_out)

    def test_chroma(self):
        out = pixelkeys.chroma((10, 20, 30))
        self.assertEqual(out, 20)

    def test_hue(self):
        gray_hue = pixelkeys.hue((20, 20, 20))
        self.assertEqual(gray_hue, 0)
        pass
