import cv2
import math
import numpy as np
import openslide
import os
import platform
import random
import subprocess
import sys
import time
import warnings

from PIL import Image


def check_compilation():

    if not os.path.isfile("src/graph_segmentation/segment"):

        # If Windows, the user must compile the script manually, otherwise
        # we attempt to compile it
        if platform.system() == "Windows":
            print("Please compile the segmentation algorithm before"
                  "running this script. Exiting.")
            sys.exit(1)
        else:
            print("Compiling the graph segmentation algorithm...")
            try:
                subprocess.check_call(["make"],
                                      stdout=subprocess.PIPE,
                                      cwd="src/graph_segmentation/")
            except Exception:
                print("Compilation of the segmentation algorithm failed. Please compile it before running this script. Exiting.")
                sys.exit(1)


def check_image(args):

    # Check if the image can be read
    try:
        _ = openslide.OpenSlide(args.svs)
    except Exception:
        raise TypeError("Unsupported format, or file not found.")


def downsample_image(slide, downsampling_factor, mode="numpy"):
    '''
    Takes an OpenSlide SVS object and downsamples the original resolution
    (level 0) by the requested downsampling factor, using the most convenient
    image level. Returns numpy array or PIL image.
    '''

    # Get the best level to quickly downsample the image
    # Add a pseudofactor of 0.1 to ensure getting the next
    # best level (i.e. if 16x is chosen, avoid getting 4x instead
    # of 16x)
    best_downsampling_level = slide.get_best_level_for_downsample(downsampling_factor + 0.1)

    # Get the image at the requested scale
    svs_native_levelimg = slide.read_region((0, 0), 
        best_downsampling_level, slide.level_dimensions[best_downsampling_level])
    target_size = tuple([int(x//downsampling_factor) for x in slide.dimensions])
    img = svs_native_levelimg.resize(target_size)

    # By default, return numpy array,
    # otherwise, return PIL image
    if mode == "numpy":
        # Remove the alpha channel
        img = np.array(img.convert("RGB"))

    return img, best_downsampling_level


def isPowerOfTwo(n):
    return math.ceil(math.log2(n)) == math.floor(math.log2(n))


def bg_color_identifier(mask, lines_pct, borders, corners):
    '''
    Identifies the background color
    '''
    bord = np.empty((1, 3))

    # Transform image percentages into number of lines
    lines_topbottom = round(mask.shape[0] * (lines_pct/100))
    lines_leftright = round(mask.shape[1] * (lines_pct/100))
            
    if borders != '0000':
        if borders[0] == '1':
            top = mask[:lines_topbottom, :, :]
            a = np.unique(top.reshape(-1, top.shape[2]), axis=0)
            bord = np.concatenate((bord, a), axis=0)
        if borders[2] == '1':
            bottom = mask[(mask.shape[0] - lines_topbottom):mask.shape[0], :, :]
            c = np.unique(bottom.reshape(-1, bottom.shape[2]), axis=0)
            bord = np.concatenate((bord, c), axis=0)
        if borders[1] == '1':
            left = mask[:, :lines_leftright, :]
            b = np.unique(left.reshape(-1, left.shape[2]), axis=0)
            bord = np.concatenate((bord, b), axis=0)
        if borders[3] == '1':
            right = mask[:, (mask.shape[1] - lines_leftright):mask.shape[1], :]
            d = np.unique(right.reshape(-1, right.shape[2]), axis=0)
            bord = np.concatenate((bord, d), axis=0)

        bord = bord[1:, :]
        bord_unique = np.unique(bord.reshape(-1, bord.shape[1]), axis=0)
        bg_color = bord_unique[0]

    if corners != '0000':
        if corners[0] == '1':
            top_left = mask[:lines_topbottom, :lines_leftright, :]
            a = np.unique(top_left.reshape(-1, top_left.shape[2]), axis=0)
            bord = np.concatenate((bord, a), axis=0)
        if corners[1] == '1':
            bottom_left = mask[(mask.shape[0] -
                                lines_topbottom):mask.shape[0], :lines_leftright, :]
            b = np.unique(bottom_left.reshape(-1, bottom_left.shape[2]),
                            axis=0)
            bord = np.concatenate((bord, b), axis=0)
        if corners[2] == '1':
            bottom_right = mask[(mask.shape[0] - lines_topbottom):mask.shape[0], (
                mask.shape[1] - lines_leftright):mask.shape[1], :]
            c = np.unique(bottom_right.reshape(-1, bottom_right.shape[2]),
                            axis=0)
            bord = np.concatenate((bord, c), axis=0)
        if corners[3] == '1':
            top_right = mask[:lines_topbottom, (mask.shape[1] -
                                                lines_leftright):mask.shape[1], :]
            d = np.unique(top_right.reshape(-1, top_right.shape[2]),
                            axis=0)
            bord = np.concatenate((bord, d), axis=0)

        bord = bord[1:, :]
        bord_unique = np.unique(bord.reshape(-1, bord.shape[1]), axis=0)
        bg_color = bord_unique[0]

    return bg_color, bord_unique


def selector(mask_patch, thres, bg_color):
    '''
    classifies a tile to be selected or not
    '''
    bg = mask_patch == bg_color
    # bg = bg.view(dtype=np.int8)

    bg_proportion = np.sum(bg) / bg.size
    if bg_proportion <= (1 - thres):
        output = 1
    else:
        output = 0

    return output


def clean(slide):

    if slide.method == "graph" or slide.method == "graphtestmode":
        if not slide.save_mask:
            os.remove(slide.img_outpath + "segmented_" + slide.sample_id + ".ppm")
        if not slide.save_edges:
            os.remove(slide.img_outpath + "edges_" + slide.sample_id + ".ppm")