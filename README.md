Pixelating images
===================================

#### Features: ####
* Control of granularity
* Color palettes


####Requirements:####
* python 2.x
* PIL (Python Imaging Library)
* python-colormath (http://python-colormath.readthedocs.org/en/latest/index.html)

##Details:###

This works by simply dividing the image in equal sized blocks and assigning them the average color of the block

####Usage:####

    usage: pixel_art.py [-h] -f FILENAME [-p {3,8,9,24}] [-n NCOLORS]
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

     
####Examples:####

![eg](https://raw.githubusercontent.com/AlexPnt/pixel-art/master/img/globe_pixelated_g2_p3.png)

![eg](https://raw.githubusercontent.com/AlexPnt/pixel-art/master/img/tennessee_pixelated_p9_g2.png)

