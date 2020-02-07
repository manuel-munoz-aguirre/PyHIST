from PIL import Image
import openslide
import numpy as np
import cv2
import warnings
import subprocess
import sys
import time
import math
import random

def downsample_image(svs, downsampling_factor, mode="numpy"):
    '''
    Takes an OpenSlide SVS object and downsamples the original resolution
    (level 0) by the requested downsampling factor, using the most convenient
    image level. Returns numpy array or PIL image.
    '''

    # Get the best level to quickly downsample the image
    # Add a pseudofactor of 0.1 to ensure getting the next
    # best level (i.e. if 16x is chosen, avoid getting 4x instead
    # of 16x)
    best_downsampling_level = svs.get_best_level_for_downsample(
        downsampling_factor + 0.1)

    # Get the image at the requested scale
    svs_native_levelimg = svs.read_region((0, 0),
                                          best_downsampling_level,
                                          svs.level_dimensions[best_downsampling_level])
    target_size = tuple([int(x//downsampling_factor) for x in svs.dimensions])
    img = svs_native_levelimg.resize(target_size)

    # By default, return numpy array,
    # otherwise, return PIL image
    if mode == "numpy":
        # Remove the alpha channel
        img = np.array(img.convert("RGB"))

    return img, best_downsampling_level


def produce_edges(args, out_img):
    '''
    Takes as input an image and uses the canny edge detector from OpenCV
    library to produce an image in which the detected edges are marked.

    Args:
        args: HistologySegment input arguments.
        out_img (str): Relative path to store the output edge image.

    Returns:
        None
    '''

    print("== Step 1: Producing edge image... ==")
    ts = time.time()

    # Read the image
    svs = openslide.OpenSlide(args.svs)
    img, bdl = downsample_image(svs, args.mask_downsample)

    if args.verbose:
        print("Requested " + str(args.mask_downsample) +
              "x downsampling for edge detection.")
        print("SVS level 0 dimensions:", svs.dimensions)
        print("Using level " + str(bdl) + " to downsample.")
        print("Downsampled size: " + str(img.shape[::-1][1:3]))

    # Run Canny edge detector
    edges = cv2.Canny(img, 100, 200)

    # Save the produced image in PPM format to give to the
    # segmentation algorithm
    edges = Image.fromarray(edges)
    warnings.filterwarnings("ignore")

    edges = edges.convert('RGB')
    edges.save(out_img, 'PPM')
    warnings.filterwarnings("default")
    te = time.time()

    if args.verbose:
        print("Elapsed time: " + str(round(te-ts, ndigits = 3)) + "s")


def produce_test_image(image, out_folder, args):
    '''
    Produces a PNG version of the segmented PPM image overlaying the
    grid with the selected patch size at the output downscale resolution.

    Args:
        image (str): Sample name (filename without extension).
        out_folder (str): Output folder for the test image.
        args: HistologySegment input arguments.

    Returns:
        None.
    '''

    print("Producing test image...")

    # Get information about arguments and image
    test_downsample = args.test_downsample
    patch_size = args.patch_size
    svs = openslide.OpenSlide(args.svs)
    image_dims = svs.dimensions  # (x, y)
    border_pct = args.pct_bc / 100
    
    # Since we read an numpy array, we need to change BGR -> RGB
    mask = cv2.imread(out_folder + "segmented_" + image + ".ppm")  # (y, x)
    resized_mask = cv2.resize(mask, (image_dims[0]//test_downsample,
                                     image_dims[1]//test_downsample))

    # Draw a grid over the image
    x_shift, y_shift = patch_size, patch_size
    gcol = [255, 0, 0]
    resized_mask[:, ::y_shift, :] = gcol
    resized_mask[::x_shift, :, :] = gcol

    # Calculate the border percentage
    hpct = round(resized_mask.shape[0] * border_pct)
    wpct = round(resized_mask.shape[1] * border_pct)

    # Draw top and bottom borders
    gcol = [0, 0, 0]
    width_range = range(wpct, resized_mask.shape[1] - wpct)
    resized_mask[hpct, width_range, :] = gcol
    resized_mask[resized_mask.shape[0] - hpct, width_range, :] = gcol

    # Draw left and right borders
    height_range = range(hpct, resized_mask.shape[0] - hpct)
    resized_mask[height_range, wpct, :] = gcol
    resized_mask[height_range, resized_mask.shape[1] - wpct, :] = gcol
    
    # The mask should have the scaling factor of the requested output image
    cv2.imwrite(out_folder + "test_" + image + ".png", resized_mask)


def produce_segmented_image(sample_id, out_folder, args):
    '''
    Invokes a shell process to run the graph-based segmentation
    algorithm with the PPM image containing the edges from the Canny detector.

    Args:
        sample_id (str): Sample name (filename without extension).
        out_folder (str): Output folder.
        args: HistologySegment input arguments.

    Returns:
        None
    '''
    print("\n== Step 2: Segmentation over the mask ==")

    ts = time.time()
    bashCommand = "src/graph_segmentation/segment " + str(args.sigma) + \
        " " + str(args.k_const) + " " + str(args.minimum_segmentsize) + " " + \
        out_folder + "edges_" + sample_id + ".ppm" + " " + \
        out_folder + "segmented_" + sample_id + ".ppm"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    te = time.time()

    if args.verbose:
        print("Elapsed time: " + str(round(te-ts, ndigits = 3)) + "s")

    if error is not None:
        print(error)
        sys.exit(1)


def randomSampler(args, img_outpath):

    # Read image and mask
    svsimg = openslide.OpenSlide(args.svs)
    n_samples = args.npatches
    patch_size = args.patch_size
    output_downsample = args.output_downsample
    
    # Find best layer for downsampling
    level0_dimensions = svsimg.dimensions

    # At the optimal downsampling level, we need to calculate
    # a correction factor for the patch size
    level = svsimg.get_best_level_for_downsample(output_downsample + 0.1)
    bestlevel_downsample = svsimg.level_downsamples[level]
    bestlevel_patchsize = int(round(output_downsample/bestlevel_downsample, ndigits = 1)*patch_size)

    # Calculate boundary pixel (top left pixel in
    # lower right corner) at the best level for downsampling
    boundary_pixel = [x - bestlevel_patchsize for x in svsimg.level_dimensions[level]]

    # Subsample pixels at level 0
    pixel_pairs = zip(random.sample(range(0, boundary_pixel[0]), n_samples),
                      random.sample(range(0, boundary_pixel[1]), n_samples))

    # The specified patch_size is at output_downsample level.
    # Need to calculate the patch size at level 0
    upsample_patchsize = patch_size * output_downsample 
    upscale_factor = round(bestlevel_downsample, ndigits = 1)

    # Start patch extraction
    digits_padding = len(str(n_samples))
    k = 0

    for w, h in list(pixel_pairs):
        w_upscale, h_upscale = int(w*upscale_factor), int(h*upscale_factor)
        img = svsimg.read_region((w_upscale, h_upscale),
                                 level,
                                 (bestlevel_patchsize, bestlevel_patchsize))

        # Resize if necessary. This condition will be true
        # when downsampling is not required.
        if bestlevel_patchsize != patch_size:
            img = img.resize((patch_size, patch_size))

        # Save patch
        img.save(img_outpath + str(k).zfill(digits_padding) +
                 "." + args.format)

        # Print progress
        if (k+1) % 25 == 0 and args.verbose:
            sys.stdout.write(str(int((k+1)/n_samples*100)) + "%" + "\r")

        k += 1

        
def isPowerOfTwo(n):
    return math.ceil(math.log2(n)) == math.floor(math.log2(n))
