#This is not the final version

'''
This python script takes as input an image and uses Canny edge detector from opencv library
to produce an image in which the detected edges are marked.
'''

#import required libraries
import numpy as np
import cv2
import sys
import openslide
from PIL import Image

#Function capable of transforming rgba to rgb
#source: https://code.i-harness.com/en/q/8bde40
def alpha_to_color(image, color=(255, 255, 255)):
    """
    Alpha composite an RGBA Image with a specified color.
    Simpler, faster version than the solutions above.
    Source: http://.com/a/9459208/284318
    Keyword Arguments:
        image -- PIL RGBA Image object
        color -- Tuple r, g, b (default 255, 255, 255)
    """
    image.load()  # needed for split()
    background = Image.new('RGB', image.size, color)
    background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
    return background

#read input, output file names and the specified level of the svs from the command line arguments
in_img = str(sys.argv[1]) 
out_img = str(sys.argv[2])
level = int(sys.argv[3])

#read the image and apply Canny edge detector
svs = openslide.OpenSlide(in_img)
img = np.array(alpha_to_color(svs.read_region((0,0), level, svs.level_dimensions[level])))
edges = cv2.Canny(img, 100, 200)

#save the produced image
cv2.imwrite(out_img, edges)
