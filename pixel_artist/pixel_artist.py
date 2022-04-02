#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging.config
import pickle
import sys

from PIL import Image
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie1976
from colormath.color_objects import LabColor, sRGBColor

from settings import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def pixelate(im, granularity, ncolors, nbits, colordiff, verbose):
	width, height = im.size[0], im.size[1]
	logger.debug(f"Input image dimensions -> {width=}, {height=}")

	block_width = find_block_dim(granularity, width)  # find the possible block dimensions
	block_height = find_block_dim(granularity, height)
	logger.debug(f"Block dimensions -> {block_width=}, {block_height=}")

	grid_width = width // block_width  # dimension of the grid
	grid_height = height // block_height
	logger.debug(f"Grid dimensions -> {grid_width=}, {grid_height=}")

	nblocks = grid_width * grid_height  # number of blocks
	logger.debug(f"Number of blocks -> {nblocks=}")

	logger.info(f"Fetching image blocks")
	blocks = []
	for n in range(nblocks):  # get all the image blocks
		blocks += [get_block(im, n, block_width, block_height)]

	logger.info("Building pixelated image ...")
	new_image = im.copy()
	for n in range(int(nblocks)):
		if verbose:
			logger.info(f"{(n / nblocks * 100):.2f}%")

		# define the target box where to paste the new block
		i = (n % grid_width) * block_width  # i,j -> upper left point of the target image
		j = n // grid_width * block_height
		box = (i, j, i + block_width, j + block_height)

		# compute the average color of the block
		avg = avg_color(blocks[n], nbits, colordiff)

		# paste it
		new_image.paste(avg, box)

	pixelated_im = new_image.convert("P", palette=Image.ADAPTIVE, colors=ncolors)
	return pixelated_im


# find the dimension(height or width) according to the desired granularity (a lower granularity small blocks)
def find_block_dim(granularity, dim):
	assert (granularity > 0)
	candidate = 0
	block_dim = 1
	counter = 0
	while counter != granularity:  # while we dont achieve the desired granularity
		candidate += 1
		while ((dim % candidate) != 0):
			candidate += 1
			if candidate > dim:
				counter = granularity - 1
				break

		if candidate <= dim:
			block_dim = candidate  # save the current feasible length

		counter += 1

	assert (dim % block_dim == 0 and block_dim <= dim)
	return block_dim


# get a block of the image
def get_block(im, n, block_width, block_height):
	width = im.size[0]

	grid_width = width / block_width  # dimension of the grid

	i = (n % grid_width) * block_width  # i,j -> upper left point of the target block
	j = (n / grid_width) * block_height

	box = (i, j, i + block_width, j + block_height)
	block_im = im.crop(box)
	return block_im


# returns the average color of a given image
def avg_color(im, nbits, colordiff):
	avg_r = avg_g = avg_b = 0.0
	pixels = im.getdata()
	size = len(pixels)
	for p in pixels:
		avg_r += p[0] / float(size)
		avg_g += p[1] / float(size)
		avg_b += p[2] / float(size)

	if nbits != 24:
		try:
			palette = pickle.load(open("palette/" + str(nbits) + "bit.palette", "rb"))
		except Exception:
			logger.exception(f"An error has occurred while loading color palette")
			sys.exit()
		best_color = palette[0]
		best_diff = colordiff(best_color, (avg_r, avg_g, avg_b))
		for i in range(1, len(palette)):
			candidate_diff = colordiff(palette[i], (avg_r, avg_g, avg_b))
			if candidate_diff < best_diff:
				best_diff = candidate_diff
				best_color = palette[i]

		return best_color
	else:
		return int(avg_r), int(avg_g), int(avg_b)


# calculate color difference of two pixels in the RGB space
# the less the better
def colordiff_rgb(pixel1, pixel2):
	delta_red = pixel1[0] - pixel2[0]
	delta_green = pixel1[1] - pixel2[1]
	delta_blue = pixel1[2] - pixel2[2]

	fit = delta_red ** 2 + delta_green ** 2 + delta_blue ** 2
	return fit


# http://python-colormath.readthedocs.org/en/latest/index.html
# calculate color difference of two pixels in the L*ab space
# the less the better
# pros: better results, cons: very slow
def colordiff_lab(pixel1, pixel2):
	# convert rgb values to L*ab values
	rgb_pixel_source = sRGBColor(pixel1[0], pixel1[1], pixel1[2], True)
	lab_source = convert_color(rgb_pixel_source, LabColor)

	rgb_pixel_palette = sRGBColor(pixel2[0], pixel2[1], pixel2[2], True)
	lab_palette = convert_color(rgb_pixel_palette, LabColor)

	# calculate delta e
	delta_e = delta_e_cie1976(lab_source, lab_palette)
	return delta_e


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Pixel art', epilog="A fun toy.")
	parser.add_argument("-f", "--filename", nargs=1, help="input filename", required=True)
	parser.add_argument("-p", "--nbits", nargs=1, help="number of bits of the palette, default=24",
						choices=[3, 8, 9, 24], type=int, default=[24])
	parser.add_argument("-n", "--ncolors", nargs=1, help="number of colors to use: 1-256, default=256", type=int,
						default=[256])
	parser.add_argument("-g", "--granularity", nargs=1,
						help="granularity to be used (>0):  a bigger value means bigger blocks, default=1", type=int,
						default=[1])
	parser.add_argument("-l", "--labdiff", help="use *lab model, default=rgb", action='store_true', default=False)
	parser.add_argument("-v", "--verbose", help="show progress", action='store_true', default=False)
	parser.add_argument("-s", "--save", help="save the output image", action='store_true', default=False)

	args = vars(parser.parse_args())
	filename = args['filename'][0]
	nbits = args['nbits'][0]
	ncolors = args['ncolors'][0]
	granularity = args['granularity'][0]
	colordiff = colordiff_rgb if not args['labdiff'] else colordiff_lab
	verbose = args['verbose']
	save = args['save']

	if filename.split(".")[-1] == "png":
		print("File format not supported. Try with a .jpg")
		sys.exit()
	if ncolors < 1 or ncolors > 256:
		parser.print_help()
		sys.exit()
	if granularity < 1:
		parser.print_help()
		sys.exit()

	try:
		im = Image.open(filename)
	except Exception as e:
		print(f"An error has occurred: {e}")
		sys.exit()
	new_image = pixelate(im, granularity, ncolors, nbits, colordiff, verbose)
	new_image.show()
	if save:
		print("saving to " + filename.split(".")[0] + "_pixelated.png ...")
		new_image.save(filename.split(".")[0] + "_pixelated.png")
