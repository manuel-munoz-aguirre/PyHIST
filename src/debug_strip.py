import pandas as pd
import numpy as np
from PIL import Image, ImageDraw
import openslide
from openslide import deepzoom
import cv2
import os
import math
from pathlib import Path

patchsize = 128
outpath = "testout/"

svsimg = openslide.OpenSlide("test_resources/GTEX-1117F-0125.svs")
dzg = deepzoom.DeepZoomGenerator(svsimg,
                                 tile_size=patchsize,
                                 overlap=0)

dzg_levels = [2**i for i in range(0, dzg.level_count)][::-1]

# Stripping image for the last 7 levels
for i in range(len(dzg_levels)-1,  len(dzg_levels)-1-7, -1):
    downsample_level = dzg_levels[i]
    tiledims = dzg.level_tiles[i]

    # Create directory for tiles
    current_path = outpath + "downsample_" + str(downsample_level) + "/"
    Path(current_path).mkdir(parents=True, exist_ok=True)

    print("=====")
    print(downsample_level)
    print(tiledims)

    if downsample_level != 8:
        continue

    k = 0
    for row in range(0, tiledims[1]):
        for col in range(0, tiledims[0]):
            # c = str(tiledims[0]*col + row + 1).rjust(5, '0')

            print(dzg.get_tile_coordinates(i, (col, row)))
            break
            
            tile = dzg.get_tile(i, (col, row))
            tile.save(current_path + str(k).rjust(5, '0') + ".jpg")
            k+=1

