import random
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
patch_size = 1000
output_downsample = 16

# Find best layer for downsampling
level0_dimensions = svsimg.dimensions

# The specified patch_size is at output_downsample level.
# Need to calculate the patch size at level 0
upsample_patchsize = patch_size * output_downsample 

# Calculate boundary pixel (top left pixel in
# lower right corner)
# TODO : HAS TO BE CALCULATED AT THE DOWNSAMPLE LEVEL,
# AND THEN UPSCALE
boundary_pixel = [x - upsample_patchsize for x in level0_dimensions]

# Subsample pixels at level 0
pixel_pairs = zip(random.sample(range(0, boundary_pixel[0]), n_samples),
                  random.sample(range(0, boundary_pixel[1]), n_samples))

# At the optimal downsampling level, we need to calculate
# a correction factor for the patch size
level = svsimg.get_best_level_for_downsample(output_downsample + 0.1)
bestlevel_downsample = svsimg.level_downsamples[level]
bestlevel_patchsize = int(round(output_downsample/bestlevel_downsample, ndigits = 2)*patch_size)

for w, h in pixel_pairs:
    img = svsimg.read_region((32922, 4533), level, (bestlevel_patchsize, bestlevel_patchsize))

    # Resize if necessary. This condition will be true
    # when downsampling is not required.
    if bestlevel_patchsize != patch_size:
        img = img.resize((patch_size, patch_size))
