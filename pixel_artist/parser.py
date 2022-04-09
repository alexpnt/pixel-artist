import argparse
import sys


def build_parser():
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

	return parser


def validate_args(parser, args):
	filename = args['filename'][0]
	nbits = args['nbits'][0]
	ncolors = args['ncolors'][0]
	granularity = args['granularity'][0]
	colordiff_fn = "colordiff_rgb" if not args['labdiff'] else "colordiff_lab"
	verbose =args["verbose"]
	save = args["save"]

	valid = True
	error_msg = ""
	if filename.split(".")[-1] == "png":
		error_msg = "File format not supported. Try with a .jpg"
		valid = False
	elif ncolors < 1 or ncolors > 256:
		error_msg = "Number of colors should be an integer between 1 and 256"
		valid = False
	elif granularity < 1:
		error_msg = "Granularity should be number greater or equal to 1"
		valid = False
	if not valid:
		if error_msg:
			sys.stdout.write(error_msg)
		parser.print_help()
		sys.exit()

	validated_args = {
		"filename": filename,
		"nbits": nbits,
		"ncolors": ncolors,
		"granularity": granularity,
		"colordiff_fn": colordiff_fn,
		"verbose": verbose,
		"save": save
	}
	return validated_args


def parse_args(parser):
	args = vars(parser.parse_args())
	args = validate_args(parser, args)
	return args
