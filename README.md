# Pixel Artist: Turn images into beautiful pixelated images 

**Pixel Artist** is a command line tool that allows the creation of pixelated
images with customizable levels of granularity (size of the visible pixels). 
Turning images into beautiful works of art that bring back nostalgic feelings 
from the early days of computer graphics is now easy as calling a single command.


## Requirements

* [Python 3.6+](https://www.python.org/)
* [Pillow](https://github.com/python-pillow/Pillow)
* [colormath](https://github.com/gtaylor/python-colormath)

## Features
* Block granularity
* Color palettes
* Color spaces (RGB and L\*a\*b) 
* Number of colors

## Usage

    usage: pixel_artist.py [-h] -f FILENAME [-p {3,8,9,24}] [-n NCOLORS]
                        [-g GRANULARITY] [-l] [-v] [-s]

    optional arguments:
      -h, --help            show this help message and exit
      -f FILENAME, --filename FILENAME
                            input filename
      -p {3,8,9,24}, --nbits {3,8,9,24}
                            number of bits of the palette, default=24
      -n NCOLORS, --ncolors NCOLORS
                            number of colors to use: 1-256, default=256
      -g GRANULARITY, --granularity GRANULARITY
                            granularity to be used (>0): a bigger value means
                            bigger blocks, default=1
      -l, --labdiff         use *lab model, default=rgb
      -v, --verbose         show progress
      -s, --save            save the output image

     
##  Examples

![eg](https://raw.githubusercontent.com/AlexPnt/pixel-art/master/img/globe_pixelated_g2_p3.png)

![eg](https://raw.githubusercontent.com/AlexPnt/pixel-art/master/img/tennessee_pixelated_p9_g2.png)

## Implementation details

The pixel-artist command line tool works by dividing the image in equal sized blocks 
and assigning them the average color of the block. 
Optionally, the size of the blocks can be configured as well the available colors.

## Contributing

[Github issues](https://github.com/alexpnt/pixel-artist/issues) are open for feature requests and bug reports. Feel free to submit a [pull request](https://github.com/alexpnt/pixel-artist/pulls) with your enhancement proposal.