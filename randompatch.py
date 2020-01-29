import pandas as pd
import numpy as np
import openslide
import cv2
from PIL import Image, ImageDraw
from openslide import deepzoom
from src import utility_functions

# Read image and mask
svsimg = openslide.OpenSlide("../imgdata/input/GTEX-1117F-0126.svs")
mask = cv2.imread("output/GTEX-1117F-0126/segmented_GTEX-1117F-0126.ppm")
n_samples = 100
mode = "random"
patch_size = 512
output_downsample = 16

# Find best layer for downsampling
target_dimensions = tuple([x//output_downsample for x in svsimg.dimensions])
level = svsimg.get_best_level_for_downsample(output_downsample + 0.1)
level_dimensions = svsimg.level_dimensions[level]

# Find maximal top layer pixel (lower right bound)
correction_factor = round(svsimg.level_downsamples[level]/output_downsample, ndigits=1)
