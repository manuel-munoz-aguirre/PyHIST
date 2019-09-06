import pandas as pd
import numpy as np
import openslide
from openslide import deepzoom
import cv2
from PIL import Image
import os
import math
import matplotlib.pyplot as plt


def bg_color_identifier(mask, lines, borders, corners):
    '''
    Identifies the background color
    '''
    bord = np.empty((1, 3))

    if borders != '0000':
        if borders[0] == '1':
            top = mask[:lines, :, :]
            a = np.unique(top.reshape(-1, top.shape[2]), axis=0)
            bord = np.concatenate((bord, a), axis=0)
        if borders[2] == '1':
            bottom = mask[(mask.shape[0] - lines):mask.shape[0], :, :]
            c = np.unique(bottom.reshape(-1, bottom.shape[2]), axis=0)
            bord = np.concatenate((bord, c), axis=0)
        if borders[1] == '1':
            left = mask[:, :lines, :]
            b = np.unique(left.reshape(-1, left.shape[2]), axis=0)
            bord = np.concatenate((bord, b), axis=0)
        if borders[3] == '1':
            right = mask[:, (mask.shape[1] - lines):mask.shape[1], :]
            d = np.unique(right.reshape(-1, right.shape[2]), axis=0)
            bord = np.concatenate((bord, d), axis=0)

        bord = bord[1:, :]
        bord_unique = np.unique(bord.reshape(-1, bord.shape[1]), axis=0)
        bg_color = bord_unique[0]

    if corners != '0000':
        if corners[0] == '1':
            top_left = mask[:lines, :lines, :]
            a = np.unique(top_left.reshape(-1, top_left.shape[2]), axis=0)
            bord = np.concatenate((bord, a), axis=0)
        if corners[1] == '1':
            bottom_left = mask[(mask.shape[0] -
                                lines):mask.shape[0], :lines, :]
            b = np.unique(bottom_left.reshape(-1, bottom_left.shape[2]),
                          axis=0)
            bord = np.concatenate((bord, b), axis=0)
        if corners[2] == '1':
            bottom_right = mask[(mask.shape[0] - lines):mask.shape[0], (
                mask.shape[1] - lines):mask.shape[1], :]
            c = np.unique(bottom_right.reshape(-1, bottom_right.shape[2]),
                          axis=0)
            bord = np.concatenate((bord, c), axis=0)
        if corners[3] == '1':
            top_right = mask[:lines, (mask.shape[1] -
                                      lines):mask.shape[1], :]
            d = np.unique(top_right.reshape(-1, top_right.shape[2]),
                          axis=0)
            bord = np.concatenate((bord, d), axis=0)

        bord = bord[1:, :]
        bord_unique = np.unique(bord.reshape(-1, bord.shape[1]), axis=0)
        bg_color = bord_unique[0]

    return bg_color, bord_unique


# Read the image
wsi_path = "test_resources/GTEX-1117F-0125.svs"

# Open mask image
mask = cv2.imread("output/GTEX-1117F-0125/segmented_GTEX-1117F-0125.ppm")

# Identify background colors
bg_color, bord = bg_color_identifier(mask, 50, '1111', '0000')

# If we detect more than one background color, then we replace them all
# with the first detected background color
if bord.shape[0] > 1:
    for i in range(1, bord.shape[0]):
        mask[np.where((mask == bord[i]).all(axis=2))] = bg_color

# Open SVS file
svs = openslide.OpenSlide(wsi_path)
image_dims = svs.dimensions

dzg = deepzoom.DeepZoomGenerator(svs,
                                 tile_size=512,
                                 overlap=0)

# Find the deep zoom level corresponding to the
# requested downsampling factor
output_downsample = 16
mask_downsample = 32
verbose = True
patch_size = 512

dzg_levels = [2**i for i in range(0, dzg.level_count)][::-1]
dzg_selectedlevel_idx = dzg_levels.index(output_downsample)
dzg_selectedlevel_dims = dzg.level_dimensions[dzg_selectedlevel_idx]
dzg_selectedlevel_maxtilecoords = dzg.level_tiles[dzg_selectedlevel_idx]
n_tiles = np.prod(dzg_selectedlevel_maxtilecoords)
dzg_real_downscaling = np.divide(svs.dimensions, dzg.level_dimensions)[
    :, 0][dzg_selectedlevel_idx]

# Calculate patch size in the mask
mask_patch_size = int(np.ceil([patch_size / output_downsample]))

if verbose:
    print("Output image information: ")
    print("Requested output downsample of " + str(output_downsample) +
          "x.")
    print("Properties of selected deep zoom level:")
    print("-Real downscaling factor: " + str(dzg_real_downscaling))
    print("-Pixel dimensions: " + str(dzg_selectedlevel_dims))
    print("-Selected patch size: " + str(patch_size))
    print("-Max tile coordinates: " + str(dzg_selectedlevel_maxtilecoords))
    print("-Number of tiles: " + str(n_tiles))

# Counters
preds = [None] * n_tiles
row, col, i = 0, 0, 0
mask_row, mask_col = 0, 0
tile_names = []
tile_dims = []
