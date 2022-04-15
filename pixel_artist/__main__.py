"""Main entry point for the pixelation tool."""

import sys

from .constants import SUCCESS
from .core import PixelArt
from .parser import build_parser, parse_args


def main() -> None:
	"""Parses the command line arguments and runs the tool."""

	arg_parser = build_parser()
	args = parse_args(arg_parser)

	pixel_art = PixelArt(args['filename'],
						 args['granularity'],
						 args['ncolors'],
						 args['nbits'],
						 args["color_space"],
						 args['verbose'])

	pixelated_image = pixel_art.pixelate()
	pixelated_image.show()
	if args['save']:
		if args['verbose']:
			print("Saving to " + args['filename'].split(".")[0] + "_pixelated.png ...")
			pixelated_image.save(args['filename'].split(".")[0] + "_pixelated.png")
	if args['verbose']:
		print('Done')

	return SUCCESS


if __name__ == "__main__":
	sys.exit(main())
