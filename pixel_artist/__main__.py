"""Main entry point for the pixelation tool."""

import sys

from .constants import SUCCESS
from .core import pixelate
from .parser import build_parser, parse_args


def main() -> None:
	"""Parses the command line arguments and bootstraps the project."""
	arg_parser = build_parser()
	args = parse_args(arg_parser)

	pixelated_image = pixelate(args['filename'],
							   args['granularity'],
							   args['ncolors'],
							   args['nbits'],
							   args["colordiff_fn"],
							   args['verbose'])
	pixelated_image.show()
	if args['save']:
		print("Saving to " + args['filename'].split(".")[0] + "_pixelated.png ...")
		pixelated_image.save(args['filename'].split(".")[0] + "_pixelated.png")

	return SUCCESS


if __name__ == "__main__":
	sys.exit(main())
