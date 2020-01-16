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


def run(sample_id, img_outpath, args):
    '''
    Chops the full resolution image to patches of a given size.
    Saves only those patches, whose 'tissue content' exceeds a threshold.
    Produces a thumbnail of the image with a cross over selected patches.
    Produces a tsv file containing patch metadata.
    '''

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

    # Open mask image as BGR
    print("\n== Step 3: Selecting tiles ==")
    ts = time.time()
    mask = cv2.imread(img_outpath + "segmented_" + sample_id + ".ppm")

    # Identify background colors from the mask
    bg_color, bord = bg_color_identifier(mask,
                                         args.lines,
                                         args.borders,
                                         args.corners)

    # If we detect more than one background color, then we replace them all
    # with the first detected background color
    if bord.shape[0] > 1:
        for i in range(1, bord.shape[0]):
            mask[np.where((mask == bord[i]).all(axis=2))] = bg_color

    # Convert to PIL
    mask = Image.fromarray(mask)

    # Open SVS file
    svs = openslide.OpenSlide(args.svs)
    image_dims = svs.dimensions

    # Create folder for the patches
    if args.save_patches:
        out_tiles = img_outpath + sample_id + "_tiles/"
        if not os.path.exists(out_tiles):
            os.makedirs(out_tiles)

    # Initialize deep zoom generator
    dzg = deepzoom.DeepZoomGenerator(svs,
                                     tile_size=args.patch_size,
                                     overlap=0)

    # Find the deep zoom level corresponding to the
    # requested downsampling factor
    dzg_levels = [2**i for i in range(0, dzg.level_count)][::-1]
    dzg_selectedlevel_idx = dzg_levels.index(args.output_downsample)
    dzg_selectedlevel_dims = dzg.level_dimensions[dzg_selectedlevel_idx]
    dzg_selectedlevel_maxtilecoords = dzg.level_tiles[dzg_selectedlevel_idx]
    dzg_real_downscaling = np.divide(svs.dimensions, dzg.level_dimensions)[
        :, 0][dzg_selectedlevel_idx]
    n_tiles = np.prod(dzg_selectedlevel_maxtilecoords)
    #digits_padding = int(math.log10(n_tiles))
    digits_padding = 6

    print(dzg_levels)
    print(dzg_selectedlevel_idx)
    print(dzg_selectedlevel_dims)
    print(dzg_selectedlevel_maxtilecoords)

    # Calculate patch size in the mask
    mask_patch_size = int(np.ceil(
        args.patch_size * (args.output_downsample/args.mask_downsample)))

    # Deep zoom generator for the mask
    dzgmask = deepzoom.DeepZoomGenerator(openslide.ImageSlide(mask),
                                         tile_size=mask_patch_size,
                                         overlap=0)
    dzgmask_dims = dzgmask.level_dimensions[dzgmask.level_count - 1]
    dzgmask_maxtilecoords = dzgmask.level_tiles[dzgmask.level_count - 1]
    dzgmask_ntiles = np.prod(dzgmask_maxtilecoords)

    # If a tile-crossed image is needed, generate a downsampled version
    # of the original one
    if args.save_tilecrossed_image:
        tilecrossed_img = utility_functions.downsample_image(
            svs, args.tilecross_downsample, mode="numpy")[0]

        # Calculate patch size in the mask
        tilecross_patchsize = int(np.ceil(
            args.patch_size * (
                args.output_downsample/args.tilecross_downsample)))

        # Draw the grid at the scaled patchsize
        x_shift, y_shift = tilecross_patchsize, tilecross_patchsize
        gcol = [255, 0, 0]
        tilecrossed_img[:, ::y_shift, :] = gcol
        tilecrossed_img[::x_shift, :, :] = gcol

        # Convert to PIL image
        tilecrossed_img = Image.fromarray(tilecrossed_img, mode="RGB")

        # Create object to draw the crosses
        draw = ImageDraw.Draw(tilecrossed_img)

        # Counters for iterating through the image
        tc_w = 0
        tc_h = 0

    if args.verbose:
        print("Original image dimensions:", str(image_dims))
        print("Output image information: ")
        print("Requested " + str(args.output_downsample) +
              "x downsampling for output.")
        print("Properties of selected deep zoom level:")
        print("-Real downscaling factor: " + str(dzg_real_downscaling))
        print("-Pixel dimensions: " + str(dzg_selectedlevel_dims))
        print("-Selected patch size: " + str(args.patch_size))
        print("-Max tile coordinates: " + str(dzg_selectedlevel_maxtilecoords))
        print("-Number of tiles: " + str(n_tiles))

        print("\nMask information: ")
        print("-Mask downscaling factor: " + str(args.mask_downsample))
        print("-Pixel dimensions: " + str(dzgmask_dims))
        print("-Calculated patch size: " + str(mask_patch_size))
        print("-Max tile coordinates: " + str(dzgmask_maxtilecoords))
        print("-Number of tiles: " + str(dzgmask_ntiles))

    # Counters
    preds = [None] * n_tiles
    row, col, i = 0, 0, 0
    tile_names = []
    tile_dims_w = []
    tile_dims_h = []
    tile_rows = []
    tile_cols = []

    # Categorize tiles using the selector function
    while row < dzg_selectedlevel_maxtilecoords[1]:

        # print("===", str(col), str(row), "===")
        # print(str(col) + "/" + str(row) + " | " + str(tc_w) + "/" + str(tc_h))

        # Extract the tile from the mask (the last level is used
        # since the mask is already rescaled)
        mask_tile = dzgmask.get_tile(dzgmask.level_count - 1, (col, row))

        # Tile converted to BGR
        mask_tile = np.array(mask_tile)

        # Predict if the tile will be kept (1) or not (0)
        preds[i] = selector(mask_tile, args.thres, bg_color)

        # Save patches if requested
        if args.save_patches:
            tile = dzg.get_tile(dzg_selectedlevel_idx, (col, row))

            # Prepare metadata
            tile_names.append(sample_id + "_" +
                              str((i)).rjust(digits_padding, '0'))
            tile_dims_w.append(tile.size[0])
            tile_dims_h.append(tile.size[1])
            tile_rows.append(row)
            tile_cols.append(col)

            # Save tile
            tile.save(out_tiles + tile_names[i] + ".jpg")

        # Draw cross over corresponding patch section
        # on tilecrossed image
        if args.save_tilecrossed_image:
            start_w = col * (tilecross_patchsize)
            start_h = row * (tilecross_patchsize)

            # print(start_w, start_h)

            # If we reach the edge of the image, we only can draw until
            # the edge pixel
            # print("target pos: ", start_w + tilecross_patchsize,
            #       "/", tilecrossed_img.size[0])

            if (start_w + tilecross_patchsize) >= tilecrossed_img.size[0]:
                cl_w = tilecrossed_img.size[0] - start_w
                # print("row jump: " + str(cl_w))
            else:
                cl_w = tilecross_patchsize

            if (start_h + tilecross_patchsize) >= tilecrossed_img.size[1]:
                cl_h = tilecrossed_img.size[1] - start_h
            else:
                cl_h = tilecross_patchsize

            # Draw the cross only if the tile has to be kept
            if preds[i] == 1:

                # From top left to bottom right
                draw.line([(start_w, start_h),
                           (start_w + cl_w, start_h + cl_h)],
                          fill=(0, 0, 255))

                # From bottom left to top right
                draw.line([(start_w, start_h + cl_h),
                           (start_w + cl_w, start_h)],
                          fill=(0, 0, 255))

            # Jump to the next tilecross tile
            tc_w = tc_w + tilecross_patchsize + 1

        # Jump to the next column tile
        col += 1

        # If we reach the right edge of the image, jump to the next row
        if col == dzg_selectedlevel_maxtilecoords[0]:
            col = 0
            row += 1

            # print("-->" + str((row, col)) + "/" +
            #       str(dzg_selectedlevel_maxtilecoords))

            if args.save_tilecrossed_image:
                tc_w = 0
                tc_h = tc_h + tilecross_patchsize + 1

        # Increase counter for metadata
        i += 1

    # Saving tilecrossed image
    if args.save_tilecrossed_image:
        tilecrossed_img.save(
            img_outpath + "/tilecrossed_" + sample_id + ".png")

    # Save predictions for each tile
    patch_results = []
    patch_results.extend(list(zip(tile_names,
                                  tile_dims_w,
                                  tile_dims_h,
                                  preds,
                                  tile_rows,
                                  tile_cols)))
    patch_results_df = pd.DataFrame.from_records(
        patch_results, columns=["Tile", "Width", "Height",
                                "Keep", "Row", "Column"])
    patch_results_df.to_csv(img_outpath + "tile_selection.tsv",
                            index=False,
                            sep="\t")

    # Finishing
    te = time.time()
    print("Elapsed time: " + str(te - ts))
