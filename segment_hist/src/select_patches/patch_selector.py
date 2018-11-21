#This is not the final version

#load the required libraries
import os
import numpy as np
import pandas as pd
import sys
import cv2
import openslide
from PIL import Image


#Function that classifies a tile to be selected or not
def selector(mask_patch, thres, bg_color):
    
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
def bg_color_identifier(mask):
    print("Identifing background...")
    top_down = mask[[x for x in (list(range(100)) + list(range((mask.shape[0] - 100), mask.shape[0])))], :, :]

    left_right = mask[:, [x for x in (list(range(100)) + list(range((mask.shape[1] - 100), mask.shape[1])))], :]

    a = np.unique(left_right.reshape(-1, left_right.shape[2]), axis=0)
    b = np.unique(top_down.reshape(-1, top_down.shape[2]), axis=0)
    borders = np.concatenate((a, b), axis=0)
    borders_unique = np.unique(borders.reshape(-1, borders.shape[1]), axis=0)
    bg_color = borders_unique[0]
    return bg_color, borders_unique

#Function capable of transforming rgba to rgb
#source: https://code.i-harness.com/en/q/8bde40
def alpha_to_color(image, color=(255, 255, 255)):
    """
    Alpha composite an RGBA Image with a specified color.
    Simpler, faster version than the solutions above.
    Source: http://.com/a/9459208/284318
    Keyword Arguments:
        image -- PIL RGBA Image object
        color -- Tuple r, g, b (default 255, 255, 255)
    """
    image.load()  # needed for split()
    background = Image.new('RGB', image.size, color)
    background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
    return background


def count_n_tiles(dims, patch_size):
    print("Counting the number of tiles...")
    width = dims[0] // patch_size
    if dims[0] % patch_size > 0: width += 1
    height = dims[1] // patch_size
    if dims[1] % patch_size > 0: height += 1
    n_tiles = width * height
    return n_tiles


def main():
    
    #Parameters
    save_tilecrossed_images = True 
    save_tiles = True
    #print(sys.argv[0])
    tissue = str(sys.argv[1])
    if len(sys.argv) > 2: 
        threshold = float(sys.argv[2])
    else:
        threshold = 0.5
    if len(sys.argv) > 3: 
        patch_size = int(sys.argv[3])
    else:
        patch_size = 512
    data_path = "image_masking/data/images/" + tissue + "/"
    masks_path = "my_project/results/segmented_images/with_edges/"
    path_tilecrossed_images = "my_project/results/patches/tiled_imagecheck/"
    output_path = "my_project/results/patches/"
    sys.stdout = open("logs/" + tissue + ".out", "a")
    sys.stderr = open("logs/" + tissue + ".error", "a")

    #List images in data
    images = sorted(os.listdir(data_path))
    if os.path.exists(output_path + tissue + "/"):
        already_done = sorted(os.listdir(output_path + tissue + "/"))

    patch_results = [] 
    print("==" + tissue + "==")
    
    for image in images:
        sample_id = image.split(".")[0]
        if "already_done" in locals():
            if sample_id in already_done:
                continue
        print("==" + sample_id + "==")

        #Download svs file
        request_code = get_image(sample_id, output_path)
        if request_code != 0:
            continue

        #Open mask image
        print("Reading mask...")
        mask = cv2.imread(masks_path + tissue + "/segmented_" + sample_id + ".ppm")

        #Identify background colors
        bg_color, borders = bg_color_identifier(mask)

        if borders.shape[0] > 1:
            for i in range(1, borders.shape[0]):
                mask[np.where((mask == borders[i]).all(axis=2))] = bg_color

        #Open svs file
        print("Reading svs file...")
        svs = openslide.OpenSlide(output_path + sample_id + ".svs")
        image_dims = svs.dimensions
        print(image_dims)

        #Resize mask to the dims of the high resolution image
        print("Resizing mask...")
        mask_zoomed = cv2.resize(mask, image_dims, interpolation = cv2.INTER_LINEAR)

        #Count the number of tiles
        n_tiles = count_n_tiles(image_dims, patch_size)
        print(str(n_tiles) + " tiles")
        digits = len(str(n_tiles)) + 1


        #create folders for image check output and the patches
        tissue_tilecrossed_path = path_tilecrossed_images + tissue + "/"
        if save_tilecrossed_images:
            if not os.path.exists(path_tilecrossed_images):
                os.makedirs(path_tilecrossed_images)
            if not os.path.exists(tissue_tilecrossed_path):
                os.makedirs(tissue_tilecrossed_path)
        if save_tiles:
            out_tiles = output_path + tissue
            if not os.path.exists(out_tiles):
                os.makedirs(out_tiles)
            out_tiles = output_path + tissue + "/" + sample_id + "/"
            if not os.path.exists(out_tiles):
                os.makedirs(out_tiles)

        preds = [None] * n_tiles
        patches = np.empty((n_tiles,), dtype=object)
        #Categorize tiles using the selector function
        print("Producing patches...")
        rows, columns, i = 0, 0, 0
        tile_names = []
        tile_dims = []
        while (columns, rows) != (0, image_dims[1]):
            width = min(patch_size, (image_dims[0] - columns))
            height = min(patch_size, (image_dims[1] - rows))
            #Extract tile from the svs file
            tile = svs.read_region((columns, rows), 0, (width, height))
            patches[i] = np.array(alpha_to_color(tile))

            tile_names.append(sample_id + "_" + str((i + 1)).rjust(digits, '0'))
            tile_dims.append(str(width) + "x" + str(height))

            #Extract the corresponing tile from the mask
            mask_patch = mask_zoomed[rows:(rows + height), columns:(columns + width), :]

            #make te prediction
            preds[i] = selector(mask_patch, threshold, bg_color)

            i += 1
            columns += width
            if columns == image_dims[0]:
                columns = 0
                rows += height

        #save patches with tissue content
        if save_tiles:
            print("Saving tiles...")
            for (idx, p) in enumerate(patches):
                if preds[idx] == 1:
                    no = str((idx + 1))
                    tile_code = no.rjust(digits, '0')
                    cv2.imwrite((out_tiles + sample_id + "_" + tile_code + ".jpg"), p)


        #write tilecrossed image:
        if save_tilecrossed_images:
            print("Producing tilecrossed image...")

            blank_canvas = Image.new("RGB", image_dims, "white")
            w = 0
            h = 0

            for (idx, p) in enumerate(patches):
                
                # If the patch is selected, we draw a cross over it
                if preds[idx] == 1:
                    cv2.line(p, (0, 0), (p.shape[0] - 1, p.shape[1] - 1), (0, 0, 255), 10)
                    cv2.line(p, (0, p.shape[1] - 1), (p.shape[0] - 1, 0), (0, 0, 255), 10)

                # Write to the canvas and change coordinates
                blank_canvas.paste(Image.fromarray(p), (w, h))
                w += p.shape[1]
                if w == image_dims[0]:
                    w = 0
                    h = h + p.shape[0]

            # Once finished, resize output image and save it
            blank_canvas.thumbnail((round(image_dims[0] * .05), round(image_dims[1] * .05)))
            blank_canvas.save(tissue_tilecrossed_path + sample_id + ".jpg")


        #Delete svs file
        print("Deleting svs file...")
        os.remove(output_path + sample_id + ".svs")

        #save preds of each image
        patch_results.extend(list(zip([tissue] * n_tiles, [sample_id] * n_tiles, tile_names, tile_dims, preds)))

    #save results in a tsv file
    patch_results_df = pd.DataFrame.from_records(patch_results, columns=["Tissue", "Sample-id", "Tile", "Dimensions", "Keep"])
    if not os.path.exists(output_path + "tile_selection.tsv"):
        patch_results_df.to_csv(output_path + "tile_selection.tsv", index=False, sep="\t")
    else:
        patch_results_df.to_csv(output_path + "tile_selection.tsv", index=False, sep="\t", mode = "a", header=False)

    print("ALL DONE!")

if __name__ == "__main__":
    main()

