Pixelating images
===================================

#### Features: ####
* Control of number of colors
* Control of granularity


####Requirements:####
* python 2.x
* PIL (Python Imaging Library)

####Usage:####

    usage: pixel_art.py [-h] -f FILENAME [-n NCOLORS] [-g GRANULARITY] [-s]

    optional arguments:
      -h, --help            show this help message and exit
      -f FILENAME, --filename FILENAME
                            input filename
      -n NCOLORS, --ncolors NCOLORS
                            number of colors to use: 1-256
      -g GRANULARITY, --granularity GRANULARITY
                            granularity to be used (>0): a bigger value means
                            bigger blocks
      -s, --save            save the output image
     
####Examples:####
**128 colors + granularity 3**
<p align="center">
  <img src="https://github.com/AlexPnt/pixel-art/blob/master/img/lane_pixelated_128.png"/>
</p>

**128 colors + granularity 3**
<p align="center">
  <img src="https://github.com/AlexPnt/pixel-art/blob/master/img/tennessee_pixelated_128.png"/>
</p>

