#This is not the final version

'''
This python script takes as input an image and uses Canny edge detector from opencv library
to produce an image in which the detected edges are marked.
'''

#import required libraries
import numpy as np
import cv2
import sys

#read input and output file names from the command line arguments
in_img = str(sys.argv[1]) 
out_img = str(sys.argv[2])

#read the image and apply Canny edge detector
img = cv2.imread(in_img)
edges = cv2.Canny(img, 100, 200)

#save the produced image
cv2.imwrite(out_img, edges)
