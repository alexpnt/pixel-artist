#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alexandre Pinto'
__version__ = "1.6"

from PIL import Image
import sys,argparse

def scramble_blocks(im,granularity,ncolors):
	width=im.size[0]
	height=im.size[1]

	block_width=find_block_dim(granularity,width)		#find the possible block dimensions
	block_height=find_block_dim(granularity,height)

	grid_width_dim=width/block_width					#dimension of the grid
	grid_height_dim=height/block_height

	nblocks=grid_width_dim*grid_height_dim				#number of blocks

	print "nblocks: ",nblocks," block width: ",block_width," block height: ",block_height
	print "getting all the blocks ..."
	blocks=[]
	for n in xrange(nblocks): #get all the image blocks
		blocks+=[get_block(im,n,block_width,block_height)]


	print "building final image ..."
	new_image=im.copy()
	for n in xrange(nblocks):
		#define the target box where to paste the new block
		i=(n%grid_width_dim)*block_width				#i,j -> upper left point of the target image
		j=(n/grid_width_dim)*block_height
		box = (i,j,i+block_width,j+block_height)	

		#compute the average color of the block
		avg=avg_color(blocks[n])

		#paste it	
		new_image.paste(avg,box)


	pixelated_im=new_image.convert("P",palette=Image.ADAPTIVE,colors=ncolors)
	return pixelated_im

#find the dimension(height or width) according to the desired granularity (a lower granularity small blocks)
def find_block_dim(granularity,dim):
	assert(granularity>0)
	candidate=0
	block_dim=1
	counter=0
	while counter!=granularity:			#while we dont achive the desired granularity
		candidate+=1
		while((dim%candidate)!=0):		
			candidate+=1
			if candidate>dim:
				counter=granularity-1
				break
		
		if candidate<=dim:
			block_dim=candidate			#save the current feasible lenght

		counter+=1

	assert(dim%block_dim==0 and block_dim<=dim)
	return block_dim

#get a block of the image
def get_block(im,n,block_width,block_height):

	width=im.size[0]
	height=im.size[1]

	grid_width_dim=width/block_width						#dimension of the grid

	i=(n%grid_width_dim)*block_width						#i,j -> upper left point of the target block
	j=(n/grid_width_dim)*block_height

	box = (i,j,i+block_width,j+block_height)
	block_im = im.crop(box)
	return block_im

#returns the average color of a given image
def avg_color(im):
	avg_r=avg_g=avg_b=0.0
	pixels=im.getdata()
	size=len(pixels)
	for p in pixels:
		avg_r+=p[0]/float(size)
		avg_g+=p[1]/float(size)
		avg_b+=p[2]/float(size)

	return (int(avg_r),int(avg_g),int(avg_b))

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Pixel art',epilog="A fun toy.")
	parser.add_argument("-f","--filename",nargs=1,help="input filename",required=True)
	parser.add_argument("-n","--ncolors",nargs=1,help="number of colors to use: 1-256, default=256",type=int,default=[256])
	parser.add_argument("-g","--granularity",nargs=1,help="granularity to be used (>0):  a bigger value means bigger blocks, default=1",type=int,default=[1])
	parser.add_argument("-s","--save",help="save the output image",action='store_true',default=False)

	args=vars(parser.parse_args())
	filename=args['filename'][0]
	ncolors=args['ncolors'][0]
	granularity=args['granularity'][0]
	save=args['save']

	if filename.split(".")[-1]=="png":
		print "File format not supported. Try with a .jpg"
		sys.exit()
	if ncolors<1 or ncolors>256:
		parser.print_help()
		sys.exit()
	if granularity<1:
		parser.print_help()
		sys.exit()

	try:
		im=Image.open(filename)
	except Exception, e:
		print "An error has ocurred: %s" %e
		sys.exit()
	new_image=scramble_blocks(im,granularity,ncolors)
	new_image.show()
	if save:
		print "saving to "+filename.split(".")[0]+"_pixelated.png ..."
		new_image.save(filename.split(".")[0]+"_pixelated.png")