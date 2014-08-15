Pixelating images
===================================

#### Features: ####
* Control of number of colors
* Control of granularity


####Requirements:####
* python 2.x
* PIL (Python Imaging Library)

##Details:###

This works by simply dividing the image in equal sized blocks and assigning them the average color of the block

####Usage:####

    usage: pixel_art.py [-h] -f FILENAME [-n NCOLORS] [-g GRANULARITY] [-s]

    optional arguments:
      -h, --help            show this help message and exit
      -f FILENAME, --filename FILENAME
                            input filename
      -n NCOLORS, --ncolors NCOLORS
                            number of colors to use: 1-256, default=256
      -g GRANULARITY, --granularity GRANULARITY
                            granularity to be used (>0): a bigger value means
                            bigger blocks, default=1
      -s, --save            save the output image
     
####Examples:####
**128 colors + granularity 4**

![eg](https://raw.githubusercontent.com/AlexPnt/pixel-art/master/img/tennessee_pixelated_4_128.png)

![eg](https://raw.githubusercontent.com/AlexPnt/pixel-art/master/img/globe_pixelated_4_128.png)

![eg](https://raw.githubusercontent.com/AlexPnt/pixel-art/master/img/lane_pixelated_4_128.png)
