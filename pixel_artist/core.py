"""Core functionality that can be used to perform pixelation of images.

This module contains the main PixelArt class, used to initialize the related objects necessary
to pixelate image objects. It also provide methods to compute and extract different types of information
from full images or blocks of image, such as the best granularity to use,
current colors and approximate block colors (averages) and color differences as well.
The end result is always an image with the same dimensions as the original input Image, but with colors updated
to reflect the pixel aesthetics.

Typical usage:
    pixel_art = PixelArt(filename,
                         granularity,
                         ncolors,
                         nbits,
                         color_space,
                         verbose)
    pixelated_image = pixel_art.pixelate()
"""

import pickle
import pkgutil
import sys
from typing import Tuple, Union

from PIL import Image
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie1976
from colormath.color_objects import LabColor, sRGBColor

from .constants import LAB


class PixelArt:
    """Main class responsible for producing pixelated images.

    Attributes:
        filename: A string containing the input image filename.
        granularity: An integer indicating the desired granularity.
        ncolors: An integer specifying the number of colors.
        nbits: An integer specifying the number of bits used to build the color palette.
        color_space: A string specifying the color space used to compute color differences.
        verbose: A boolean indicating if progress messages should be displayed.
    """

    def __init__(self, filename: str, granularity: int, ncolors: int, nbits: int, color_space: str, verbose: bool):
        """Initialization method that takes user options and builds the auxiliary information."""

        self.filename = filename
        self.granularity = granularity
        self.ncolors = ncolors
        self.nbits = nbits
        self.color_space = color_space
        self.verbose = verbose

        # create image object
        try:
            self.im = Image.open(self.filename)
        except Exception as e:
            print(f"An error while loading image: {e}")
            sys.exit()

        # load palette
        self.palette = None
        if nbits != 24:
            try:
                palette_data = pkgutil.get_data(__name__, "palette/" + str(self.nbits) + "bit.palette")
                self.palette = pickle.loads(palette_data)
            except Exception as e:
                print(f"An error has occurred while loading the color palette: {e}")
                sys.exit()

        # compute image dimensions
        self.width, self.height = self.im.size[0], self.im.size[1]
        if self.verbose:
            print(f"Input image dimensions -> width={self.width}, height={self.height}")

        # find the possible block dimensions
        assert self.granularity > 0
        self.block_width = self.find_block_dim(self.width)
        self.block_height = self.find_block_dim(self.height)
        if self.verbose:
            print(f"Block dimensions -> width={self.block_width}, height={self.block_height}")

        # dimension of the grid
        self.grid_width = self.width // self.block_width
        self.grid_height = self.height // self.block_height
        if self.verbose:
            print(f"Grid dimensions -> width={self.grid_width}, height={self.grid_height}")

        # number of blocks
        self.nblocks = self.grid_width * self.grid_height
        if self.verbose:
            print(f"Fetching {self.nblocks} image blocks")

        # fetch all the image blocks
        self.blocks = []
        for i in range(int(self.nblocks)):
            self.blocks.append(self.get_block_at_pos(i))

    # find the dimension
    def find_block_dim(self, dim: int) -> int:
        """Finds the dimension of the unit block corresponding to the input dimension (height or width),
         according to the desired granularity.
        A lower granularity means that small blocks will be used across the image.

        Args:
          dim: An integer indicating one input's image dimension.

        Returns:
            An integer representing a dimension (height or width) of the block to be used across the image.
        """
        candidate = 0
        block_dim = 1
        counter = 0
        while counter != self.granularity:  # while we dont achieve the desired granularity
            candidate += 1
            while dim % candidate != 0:
                candidate += 1
                if candidate > dim:
                    counter = self.granularity - 1
                    break

            if candidate <= dim:
                block_dim = candidate  # save the current feasible length

            counter += 1

        assert (dim % block_dim == 0 and block_dim <= dim)
        return block_dim

    def pixelate(self) -> Image:
        """Main method that contains all the high-level steps to perform pixelation of the input image.

        The pixelation is implemented by using a sliding block across the input image,
        where each region defined by the sliding block is replaced by the average block color.

        Returns:
            A PIL.Image instance, representing the pixelated image .
        """
        pixelated_im = self.im.copy()
        for i in range(int(self.nblocks)):
            if self.verbose:
                print(f"Building pixelated image:  {(i / self.nblocks * 100):.2f} %", end="\r")

            # define the target box where to paste the new block
            bbox = self.get_bbox_at_pos(i)

            # compute the average color of the block
            avg_color = tuple(round(c) for c in self.avg_color(self.blocks[i]))

            # paste it
            pixelated_im.paste(avg_color, bbox)

        if self.verbose:
            print()
        pixelated_im = pixelated_im.convert("P", palette=Image.ADAPTIVE, colors=self.ncolors)
        return pixelated_im

    # get the block at the ith position of the image
    def get_block_at_pos(self, pos: int) -> Image:
        """Gets a block of the image, specified by its index position (among the total image blocks).

        Args:
          pos: An integer indicating which image block to get.

        Returns:
            A PIL.Image instance containing an image block.
        """
        bbox = self.get_bbox_at_pos(pos)
        block_im = self.im.crop(bbox)

        return block_im

    def get_bbox_at_pos(self, pos: int) -> Tuple:
        """Gets the bounding box limits of an image block,
        specified by its index position (among the total image blocks).

        Args:
          pos: An integer indicating which image block to get the bounding box.

        Returns:
            A tuple containing the coordinate limits of the region defined by the image block.
            Each tuple position indicates a coordinate of the region and is described as:
                - [0] upper left image x coordinate
                - [1] upper left image y coordinate
                - [2] lower right image x coordinate
                - [3] lower right image y coordinate
        """
        i = (pos % self.grid_width) * self.block_width  # i,j -> upper left point of the target block
        j = (pos // self.grid_width) * self.block_height

        bbox = (i, j, i + self.block_width, j + self.block_height)

        return bbox

    def avg_color(self, im: Image) -> Tuple:
        """Computes the average color of an image.

        Args:
          im: A PIL.Image containing the image used to compute the average color.

        Returns:
            A tuple containing the 3 color values (Red, Green, Blue) representing the average color of the given image.
        """
        avg_r = avg_g = avg_b = 0.0
        pixels = im.getdata()
        size = len(pixels)

        for p in pixels:
            avg_r += p[0] / size
            avg_g += p[1] / size
            avg_b += p[2] / size

        if self.palette:
            best_color = self.palette[0]
            best_diff = self.colordiff(best_color, (avg_r, avg_g, avg_b))
            for i in range(1, len(self.palette)):
                candidate_diff = self.colordiff(self.palette[i], (avg_r, avg_g, avg_b))
                if candidate_diff < best_diff:
                    best_diff = candidate_diff
                    best_color = self.palette[i]

            return best_color
        else:
            return avg_r, avg_g, avg_b

    def colordiff(self, pixel1: Tuple, pixel2: Tuple) -> Union[int, float]:
        """Computes the difference between two pixels, defined by their respective color values.

        Args:
          pixel1: A tuple containing one pixel value.
          pixel2: A tuple containing another pixel value.

        Returns:
            A value representing the color difference between the two pixels.
            Depending if the color space used was Lab* or RGB, the output type will either be float or int.
        """
        if self.color_space == LAB:
            diff = self.colordiff_lab(pixel1, pixel2)
        else:
            diff = self.colordiff_rgb(pixel1, pixel2)
        return diff

    @staticmethod
    def colordiff_rgb(pixel1: Tuple, pixel2: Tuple) -> int:
        """Computes the color difference between two pixels, in the RGB color space.

        A small value will lead to better results.

        Args:
          pixel1: A tuple containing one pixel value.
          pixel2: A tuple containing another pixel value.

        Returns:
            An integer representing the color difference between the two pixels.
        """
        delta_red = pixel1[0] - pixel2[0]
        delta_green = pixel1[1] - pixel2[1]
        delta_blue = pixel1[2] - pixel2[2]

        fit = delta_red ** 2 + delta_green ** 2 + delta_blue ** 2
        return fit

    @staticmethod
    def colordiff_lab(pixel1: Tuple, pixel2: Tuple) -> float:
        """Computes the color difference between two pixels, in the Lab* color space.

        A small value will lead to better results.
        Working in the Lab* color space provides better accuracies, but it is a slower method.

        Args:
          pixel1: A tuple containing one pixel value.
          pixel2: A tuple containing another pixel value.

        Returns:
            A float value representing the color difference between the two pixels.
        """
        # convert rgb values to L*ab values
        rgb_pixel_source = sRGBColor(pixel1[0], pixel1[1], pixel1[2], True)
        lab_source = convert_color(rgb_pixel_source, LabColor)

        rgb_pixel_palette = sRGBColor(pixel2[0], pixel2[1], pixel2[2], True)
        lab_palette = convert_color(rgb_pixel_palette, LabColor)

        # calculate delta e
        delta_e = delta_e_cie1976(lab_source, lab_palette)
        return delta_e
