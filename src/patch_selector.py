#load required libraries
import pandas as pd
import numpy as np
import openslide
import cv2
from PIL import Image
import os

def run(sample_id, threshold, patch_size, lines, borders, corners, 
        save_tilecrossed_images, save_patches, svs_fname, level):

    '''
    Chops the full resolution image to patches of a given size.
    Saves only those patches, whose 'tissue content' exceeds a threshold.
    Produces a thumbnail of the image with a cross over selected patches.
    Produces a tsv file containing patch metadata.
    '''
    
    #Function that classifies a tile to be selected or not
    def selector(mask_patch, thres, bg_color):
        '''
        classifies a tile to be selected or not
        '''
        bg = mask_patch == bg_color
        bg = bg.view(dtype=np.int8)
        #bg = np.mean(bg, axis=2)
        bg_proportion = np.sum(bg)/bg.size
        if bg_proportion <= (1-thres):
           output = 1
        else:
           output = 0
    
        return output
    
    #Function that identifies the background color
    def bg_color_identifier(mask, lines, borders, corners):
        '''
        Identifies the background color
        '''
        print("Identifing background...")
        bord = np.empty((1,3))
    
        if borders != '0000':
            if borders[0] == '1':
                top = mask[:lines, :, :]
                a = np.unique(top.reshape(-1, top.shape[2]), axis=0)
                bord = np.concatenate((bord, a), axis=0)
            if borders[2] == '1':
                bottom = mask[(mask.shape[0] - lines) : mask.shape[0], :, :]
                c = np.unique(bottom.reshape(-1, bottom.shape[2]), axis=0)
                bord = np.concatenate((bord, c), axis=0)
            if borders[1] == '1':
                left = mask[:, :lines, :]
                b = np.unique(left.reshape(-1, left.shape[2]), axis=0)
                bord = np.concatenate((bord, b), axis=0)
            if borders[3] == '1':
                right = mask[:, (mask.shape[1] - lines) : mask.shape[1], :]
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
                bottom_left = mask[(mask.shape[0] - lines) : mask.shape[0], :lines, :]
                b = np.unique(bottom_left.reshape(-1, bottom_left.shape[2]), axis=0)
                bord = np.concatenate((bord, b), axis=0)
            if corners[2] == '1':
                bottom_right = mask[(mask.shape[0] - lines) : mask.shape[0], (mask.shape[1] - lines) : mask.shape[1], :]
                c = np.unique(bottom_right.reshape(-1, bottom_right.shape[2]), axis=0)
                bord = np.concatenate((bord, c), axis=0)
            if corners[3] == '1':
                top_right = mask[:lines, (mask.shape[1] - lines) : mask.shape[1], :]
                d = np.unique(top_right.reshape(-1, top_right.shape[2]), axis=0)
                bord = np.concatenate((bord, d), axis=0)
        
            bord = bord[1:, :]
            bord_unique = np.unique(bord.reshape(-1, bord.shape[1]), axis=0)
            bg_color = bord_unique[0]
        
        return bg_color, bord_unique
    
    def count_n_tiles(dims, patch_size):
        '''
        Counts the number of tiles the image is going to split.
        '''
        print("Counting the number of tiles...")
        width = dims[0] // patch_size
        if dims[0] % patch_size > 0: width += 1
        height = dims[1] // patch_size
        if dims[1] % patch_size > 0: height += 1
        n_tiles = width * height
        return n_tiles
    
    
    
    patch_results = [] 
    
    #Open mask image
    print("Reading mask...")
    mask = cv2.imread("segmented_" + sample_id + ".ppm")
    
    #Identify background colors
    bg_color, bord = bg_color_identifier(mask, lines, borders, corners)
    
    if bord.shape[0] > 1:
        for i in range(1, bord.shape[0]):
            mask[np.where((mask == bord[i]).all(axis=2))] = bg_color
    
    #Open svs file
    print("Reading svs file...")
    svs = openslide.OpenSlide(svs_fname)
    image_dims = svs.dimensions
    print(image_dims)
    
    #Count the number of tiles
    n_tiles = count_n_tiles(image_dims, patch_size)
    print(str(n_tiles) + " tiles")
    digits = len(str(n_tiles)) + 1
    
    #calc patch size in mask
    mask_patch_size = int(np.ceil([patch_size/svs.level_downsamples[level]]))
    
    #create folders for the patches
    if save_patches:
        out_tiles = sample_id + "_tiles/"
        if not os.path.exists(out_tiles):
            os.makedirs(out_tiles)
    
    preds = [None] * n_tiles
    #Categorize tiles using the selector function
    print("Producing patches...")

    rows, columns, i = 0, 0, 0
    mask_rows, mask_columns = 0, 0
    tile_names = []
    tile_dims = []
    
    if save_tilecrossed_images:
        blank_canvas = Image.new("RGB", (round(image_dims[0] * .05), round(image_dims[1] * .05)), "white")
        w = 0
        h = 0

    while (columns, rows) != (0, image_dims[1]):
        width = min(patch_size, (image_dims[0] - columns))
        height = min(patch_size, (image_dims[1] - rows))
        #Extract tile from the svs file
        tile = svs.read_region((columns, rows), 0, (width, height))
    
        tile_names.append(sample_id + "_" + str((i + 1)).rjust(digits, '0'))
        tile_dims.append(str(width) + "x" + str(height))
    
        #Extract the corresponing tile from the mask
        mask_width = min(mask_patch_size, (mask.shape[1] - mask_columns))
        mask_height = min(mask_patch_size, (mask.shape[0] - mask_rows))
        mask_patch = mask[mask_rows:(mask_rows + mask_height), mask_columns:(mask_columns + mask_width), :]
    
        #make te prediction
        preds[i] = selector(mask_patch, threshold, bg_color)
    
        #save patches with tissue content
        if save_patches:
            if preds[i] == 1:
                p = np.array(tile.convert('RGB'))
                p = p[...,::-1]
                cv2.imwrite((out_tiles + tile_names[i] + ".jpg"), p)
    
        #write tilecrossed image:
        if save_tilecrossed_images:
                
            p = np.array(tile.convert('RGB'))
            p = p[...,::-1]
            p = cv2.resize(p, None, fx=0.05, fy=0.05, interpolation = cv2.INTER_AREA)
    
            # If the patch is selected, we draw a cross over it
            if preds[i] == 1:
                cv2.line(p, (0, 0), (p.shape[0] - 1, p.shape[1] - 1), (0, 0, 255), 10)
                cv2.line(p, (0, p.shape[1] - 1), (p.shape[0] - 1, 0), (0, 0, 255), 10)
    
            # Write to the canvas and change coordinates
            blank_canvas.paste(Image.fromarray(p), (w, h))
            w += p.shape[1]
            if w == round(image_dims[0] * .05):
                w = 0
                h = h + p.shape[0]
    
        #move coordinates
        i += 1
        columns += width
        if columns == image_dims[0]:
            columns = 0
            rows += height

        mask_columns += mask_width
        if mask_columns == mask.shape[1]:
            mask_columns = 0
            mask_rows += mask_height

    #Save tilecrossed image
    if save_tilecrossed_images:
        blank_canvas.save("tilecrossed_" + sample_id + ".jpg")
    
    #save preds of each image
    patch_results.extend(list(zip(tile_names, tile_dims, preds)))
    
    #save results in a tsv file
    patch_results_df = pd.DataFrame.from_records(patch_results, columns=["Tile", "Dimensions", "Keep"])
    patch_results_df.to_csv("tile_selection.tsv", index=False, sep="\t")
    
    print("OK")
