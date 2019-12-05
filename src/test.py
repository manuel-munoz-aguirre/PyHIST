import pandas as pd
import numpy as np
from PIL import Image, ImageDraw
import openslide
from openslide import deepzoom
import cv2
import os
import math
import time
from src import utility_functions

svs = openslide.OpenSlide("test_resources/GTEX-1117F-3226.svs")

openslide.OpenSlide()

dzg = deepzoom.DeepZoomGenerator(svs,
                                 tile_size=64,
                                 overlap=0)

dzg_levels = [2**i for i in range(0, dzg.level_count)][::-1]
dzg_selectedlevel_idx = dzg_levels.index(16)
dzg_selectedlevel_dims = dzg.level_dimensions[dzg_selectedlevel_idx]
dzg_selectedlevel_maxtilecoords = dzg.level_tiles[dzg_selectedlevel_idx]
dzg_real_downscaling = np.divide(svs.dimensions, dzg.level_dimensions)[
    :, 0][dzg_selectedlevel_idx]
n_tiles = np.prod(dzg_selectedlevel_maxtilecoords)
digits_padding = int(math.log10(n_tiles))


rows = []
tc = 0
for row in range(0, dzg_selectedlevel_maxtilecoords[1]):
    for col in range(0, dzg_selectedlevel_maxtilecoords[0]):

        # x = dzg.get_tile(dzg_selectedlevel_idx, (col, row))
        # tile = np.array(x).shape
        args, z_size = dzg._get_tile_info(dzg_selectedlevel_idx, (col, row))
        tile = dzg._osr.read_region(*args)

        # Scale the tile to the correct size
        tile.thumbnail(z_size, Image.ANTIALIAS)
        rows.append((row, col, *tile.size))
        tile.convert('RGB').save("output/test/" +
                                 str(tc).rjust(6, '0') + ".jpg")
        tc += 1

rows = pd.DataFrame.from_records(rows, columns=["r", "c", "w", "h"])

svs.read_region

dzg.get_tile_coordinates(dzg_selectedlevel_idx, (0, 1))
svs.get_best_level_for_downsample(16)


