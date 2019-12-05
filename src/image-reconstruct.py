import pandas as pd
from PIL import Image, ImageDraw
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os

metadata_file = "output/GTEX-1117F-0125/tile_selection.tsv"
tilepath = "output/GTEX-1117F-0125/GTEX-1117F-0125_tiles/"

tiles = sorted(os.listdir(tilepath))

metadata = pd.read_csv(metadata_file, sep="\t")

# Get image dimensions
img_width = metadata.loc[metadata["Row"] == 0, "Width"].sum()
img_height = metadata.loc[metadata["Column"] == 0, "Height"].sum()
ncol = metadata["Column"].max()
nrow = metadata["Row"].max()

blank_canvas = Image.new("RGB", (img_width, img_height), "white")
w = 0
h = 0

for i in range(1, metadata.shape[0]):
    if metadata.loc[i, "Column"] < metadata.loc[i-1, "Column"]:
        metadata.loc[i-1, "Reset"] = True
    else:
        metadata.loc[i-1, "Reset"] = False
metadata.fillna(False, inplace=True)

for i in range(0, metadata.shape[0]):
    current_patch = Image.open(tilepath + metadata.loc[i, "Tile"] + ".jpg")
    blank_canvas.paste(current_patch, (w, h))
    w += metadata.loc[i, "Width"]

    if metadata.loc[i, "Reset"]:
        # print(metadata.loc[i, "Row"], metadata.loc[i, "Column"])
        print(w, h)
        h += metadata.loc[i, "Height"]
        w = 0

    # print(metadata.loc[i, "Row"], metadata.loc[i, "Column"])

blank_canvas.save("out.jpg")


with pd.option_context('display.max_rows', -1, 'display.max_columns', 5):
    print(metadata.iloc[0:100, :])
