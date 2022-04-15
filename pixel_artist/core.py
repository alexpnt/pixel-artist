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
	def __init__(self, filename: str, granularity: int, ncolors: int, nbits: int, color_space: str, verbose: bool):
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
		self.grid_width = self.width / self.block_width
		self.grid_height = self.height / self.block_height
		if self.verbose:
			print(f"Grid dimensions -> width={self.grid_width}, height={self.grid_height}")

		# number of blocks
		self.nblocks = self.grid_width * self.grid_height
		if self.verbose:
			print(f"Number of blocks -> {self.nblocks}")

		# get all the image blocks
		if self.verbose:
			print(f"Fetching image blocks")
		self.blocks = []
		for i in range(int(self.nblocks)):
			self.blocks += [self.get_ith_block(i)]

	# find the dimension(height or width) according to the desired granularity (a lower granularity small blocks)
	def find_block_dim(self, dim: int) -> int:
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
		pixelated_im = self.im.copy()
		for i in range(int(self.nblocks)):
			if self.verbose:
				print(f"Building pixelated image:  {(i / self.nblocks * 100):.2f} %", end="\r")

			# define the target box where to paste the new block
			bbox = self.get_ith_bbox(i)
			bbox = tuple(int(b) for b in bbox)

			# compute the average color of the block
			avg = self.avg_color(self.blocks[i])

			# paste it
			pixelated_im.paste(avg, bbox)
		if self.verbose:
			print()
		pixelated_im = pixelated_im.convert("P", palette=Image.ADAPTIVE, colors=self.ncolors)
		return pixelated_im

	# get the ith block of the image
	def get_ith_block(self, i: int) -> Image:
		bbox = self.get_ith_bbox(i)
		block_im = self.im.crop(bbox)
		return block_im

	def get_ith_bbox(self, i: int) -> Tuple:
		i = (i % self.grid_width) * self.block_width  # i,j -> upper left point of the target block
		j = (i / self.grid_width) * self.block_height

		bbox = (i, j, i + self.block_width, j + self.block_height)

		return bbox

	# returns the average color of a given image
	def avg_color(self, im: Image) -> Tuple:
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
			return int(avg_r), int(avg_g), int(avg_b)

	def colordiff(self, pixel1: Tuple, pixel2: Tuple) -> Union[int, float]:
		if self.color_space == LAB:
			diff = self.colordiff_lab(pixel1, pixel2)
		else:
			diff = self.colordiff_rgb(pixel1, pixel2)
		return diff

	# calculate color difference of two pixels in the RGB space
	# the less the better
	@staticmethod
	def colordiff_rgb(pixel1: Tuple, pixel2: Tuple) -> int:
		delta_red = pixel1[0] - pixel2[0]
		delta_green = pixel1[1] - pixel2[1]
		delta_blue = pixel1[2] - pixel2[2]

		fit = delta_red ** 2 + delta_green ** 2 + delta_blue ** 2
		return fit

	# http://python-colormath.readthedocs.org/en/latest/index.html
	# calculate color difference of two pixels in the L*ab space
	# the less the better
	# pros: better results, cons: very slow
	@staticmethod
	def colordiff_lab(pixel1: Tuple, pixel2: Tuple) -> float:
		# convert rgb values to L*ab values
		rgb_pixel_source = sRGBColor(pixel1[0], pixel1[1], pixel1[2], True)
		lab_source = convert_color(rgb_pixel_source, LabColor)

		rgb_pixel_palette = sRGBColor(pixel2[0], pixel2[1], pixel2[2], True)
		lab_palette = convert_color(rgb_pixel_palette, LabColor)

		# calculate delta e
		delta_e = delta_e_cie1976(lab_source, lab_palette)
		return delta_e
