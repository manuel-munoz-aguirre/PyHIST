import pandas as pd
import numpy as np
from PIL import Image, ImageDraw
import openslide
from openslide import deepzoom
import cv2
import os
import math
from pathlib import Path

# https://github.com/openslide/openslide/issues/278
# https://github.com/libvips/libvips/issues/1401
# conda install pixman=0.36.0

# python segment_hist.py --content-threshold 0.05 --sigma 0.7 --patch-size 64 --mask-downsample 16 --output-downsample 16 --tilecross-downsample 64 --verbose --save-tilecrossed-image --save-mask test_resources/GTEX-1117F-0125.svs

patchsize = 256
outpath = "testout/"
svsimg = openslide.OpenSlide("test_resources/GTEX-1117F-0125.svs")
maskpath = "output/GTEX-1117F-0125/segmented_GTEX-1117F-0125.ppm"
mask_downsample = 16
output_downsample = 32


# Reader for SVS
dzg = deepzoom.DeepZoomGenerator(svsimg,
                                 tile_size=patchsize,
                                 overlap=0)

# Initialize mask reader
mask = cv2.imread(maskpath)
mask = Image.fromarray(mask)
mask_patch_size = int(np.ceil(
    patchsize * (output_downsample/mask_downsample)))

dzgmask = deepzoom.DeepZoomGenerator(openslide.ImageSlide(mask),
                                     tile_size=mask_patch_size,
                                     overlap=0)
dzgmask_dims = dzgmask.level_dimensions[dzgmask.level_count - 1]
dzgmask_maxtilecoords = dzgmask.level_tiles[dzgmask.level_count - 1]
dzgmask_ntiles = np.prod(dzgmask_maxtilecoords)


# Scroll through the deepzoom mask, for each tile, predict,
# get the coordinates in the base layer size for the SVS.
# Need to calculate the width and height of the tile in the SVS
dzg_levels = [2**i for i in range(0, dzg.level_count)][::-1]
dzg_selectedlevel_idx = dzg_levels.index(output_downsample)

svs_level = svsimg.get_best_level_for_downsample(output_downsample + 0.1)

correction_factor = round(svsimg.level_downsamples[svs_level]/output_downsample, 1)

# Numbers must match:
print(dzg.level_tiles[dzg_selectedlevel_idx])
print(dzgmask.level_tiles[dzgmask.level_count-1])


# selected downsample level dimension
svsimg.level_dimensions[2]
dzgmask.level_dimensions


# goal size
[x/2 for x in svsimg.level_dimensions[2]]

k = 0
for row in range(0, dzgmask_maxtilecoords[1]):
    for col in range(0, dzgmask_maxtilecoords[0]):
        tile_info = dzg.get_tile_coordinates(dzg_selectedlevel_idx, (col, row))
        tile_dimensions = dzgmask.get_tile_dimensions(dzgmask.level_count-1, (col, row))

        stepsize = tuple([int(correction_factor*x) for x in tile_dimensions])

        print("Tile dimensions: " + str(tile_dimensions))
        print("Anchor:" + str(tile_info[0]) + ", step: " + str(stepsize) + "\n")
        
        tile = svsimg.read_region(tile_info[0], svs_level, stepsize)
        tile.save("testout/dump/" + str(k).rjust(5, '0') + ".png")
        k += 1



# ---------- DUMPER -----------
orig_res = svsimg.dimensions

# Dump tiles for level 2
# In [105]: level2dims
# Out[105]: (2987, 2415)
level2dims = svsimg.level_dimensions[2]

# Chop in ten pieces
tw2 = math.floor(level2dims[0] / 10)
th2 = math.floor(level2dims[1] / 10)
sw = [x for x in range(0, level2dims[0], tw2)]
sh = [x for x in range(0, level2dims[1], th2)]
tups = [(row, col) for col in sh for row in sw]


tile = svsimg.read_region((0, 1208*16), 2, (1494, 1208))
tile.save("test.png")

img = np.array(tile.convert("RGB"))


# dzg_levels = [2**i for i in range(0, dzg.level_count)][::-1]

# # Stripping image for the last 7 levels
# for i in range(len(dzg_levels)-1,  len(dzg_levels)-1-7, -1):
#     downsample_level = dzg_levels[i]
#     tiledims = dzg.level_tiles[i]

#     # Create directory for tiles
#     current_path = outpath + "downsample_" + str(downsample_level) + "/"
#     Path(current_path).mkdir(parents=True, exist_ok=True)

#     print("=====")
#     print(downsample_level)
#     print(tiledims)

#     if downsample_level != 64:
#         continue

#     k = 0
#     for row in range(0, tiledims[1]):
#         for col in range(0, tiledims[0]):


#             coords = dzg.get_tile_coordinates(i, (col, row))
#             tile = svsimg.read_region(coords[0], 0, )
            
#             tile = dzg.get_tile(i, (col, row))
#             # tile.save(current_path + str(k).rjust(5, '0') + ".jpg")
#             k+=1

