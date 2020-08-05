import cv2
import logging
import numpy as np
import os
import openslide
import pandas as pd
import random
import subprocess
import sys
import time
import warnings

from openslide import deepzoom
from PIL import Image, ImageDraw
from src import utility_functions


class PySlide:
    """A container for the slide and segmentation configuration.

    Attributes:
        initial_args: See parser for all the segmentation arguments.

        sample_id: Input filename, removing the path and extension.
        img_outpath: Path to store all the image output
        tile_folder: Path to store the output tiles.
        slide: OpenSlide object with the input slide.
    """

    def __init__(self, *initial_args, **kwargs):
        """Inits PySlide with the arguments from ArgumentParser."""

        # PyHIST init arguments are the slide properties
        for dictionary in initial_args:
            for key in dictionary:
                setattr(self, key, dictionary[key])

        for key in kwargs:
            setattr(self, key, kwargs[key])

        # The slide sample ID is the filename without the extension
        self.sample_id = os.path.splitext(os.path.basename(self.svs))[0]

        # Create the output folder for the slide
        self._create_output_folder()

        # Open the slide
        self.slide = openslide.OpenSlide(self.svs)


    def _create_output_folder(self):
        """Creates an output folder using the sample ID to hold the pipeline output."""
        # Ensure output folder has a trailing slash
        self.output = os.path.join(self.output, '')

        # Create the output folder
        if not os.path.exists(self.output):
            os.makedirs(self.output)

        # Create a folder for the sample
        self.img_outpath = os.path.join(self.output + self.sample_id, '')
        if not os.path.exists(self.img_outpath):
            os.makedirs(self.img_outpath)


    def _create_tile_folder(self):
        """Creates a subfolder in the output folder to hold individual tiles."""

        self.tile_folder = os.path.join(self.img_outpath + self.sample_id + "_tiles", '')
        if not os.path.exists(self.tile_folder):
            os.makedirs(self.tile_folder)


class TileGenerator:
    """An object to perform tile extraction.

    Attributes:
        method: The requested method to generate tiles.
        input_slide: A PySlide object.
    """

    def __init__(self, input_slide):
        """Init using PySlide and its properties."""
        self.method = input_slide.method
        self.input_slide = input_slide


    def execute(self):
        """Executes a tile-generating process."""
        if self.method == "randomsampling":
            self.__randomsampler()
        elif self.method == "graphtestmode":
            self.__graphtestmode()
        elif self.method == "graph":
            mask, bg_color = self.__graph()
            self.__create_tiles(mask, bg_color)
        elif self.method == "otsu":
            mask, bg_color = self.__otsu()
            self.__create_tiles(mask, bg_color)
        elif self.method == "adaptive":
            mask, bg_color = self.__adaptive()
            self.__create_tiles(mask, bg_color)
        else:
            raise NotImplementedError


    def __randomsampler(self):
        """Extracts tiles randomly from a slide. No content thresholding is performed."""

        logging.info("== Performing random tile sampling ==")

        # Find best layer for downsampling
        level0_dimensions = self.input_slide.slide.dimensions

        # At the optimal downsampling level, we need to calculate
        # a correction factor for the patch size
        level = self.input_slide.slide.get_best_level_for_downsample(self.input_slide.output_downsample + 0.1)
        bestlevel_downsample = self.input_slide.slide.level_downsamples[level]
        bestlevel_patchsize = int(round(self.input_slide.output_downsample/bestlevel_downsample, ndigits = 1)*self.input_slide.patch_size)

        # Calculate boundary pixel (top left pixel in
        # lower right corner) at the best level for downsampling
        boundary_pixel = [x - bestlevel_patchsize for x in self.input_slide.slide.level_dimensions[level]]

        # Subsample pixels at level 0
        pixel_pairs = zip(random.sample(range(0, boundary_pixel[0]), self.input_slide.npatches),
            random.sample(range(0, boundary_pixel[1]), self.input_slide.npatches))

        # The specified self.patch_size is at self.output_downsample level.
        # Need to calculate the patch size at level 0
        upsample_patchsize = self.input_slide.patch_size * self.input_slide.output_downsample
        upscale_factor = round(bestlevel_downsample, ndigits = 1)

        # Create folder to save the tiles
        if self.input_slide.save_patches:
            self.input_slide._create_tile_folder()

        # Start patch extraction
        digits_padding = len(str(self.input_slide.npatches))
        k = 0

        for w, h in list(pixel_pairs):
            w_upscale, h_upscale = int(w*upscale_factor), int(h*upscale_factor)
            img = self.input_slide.slide.read_region((w_upscale, h_upscale), level, (bestlevel_patchsize, bestlevel_patchsize))

            # Resize if necessary. This condition will be true
            # when downsampling is not required.
            if bestlevel_patchsize != self.input_slide.patch_size:
                img = img.resize((self.input_slide.patch_size, self.input_slide.patch_size))

            # Save patch
            if self.input_slide.save_patches:
                output_filename = self.input_slide.tile_folder + self.input_slide.sample_id + "_" + str(k).zfill(digits_padding) + "." + self.input_slide.format
                img.save(output_filename)

            # Print progress
            if (k+1) % 25 == 0 and self.input_slide.info != "silent":
                sys.stdout.write(str(int((k+1)/self.input_slide.npatches*100)) + "%" + "\r")
            k += 1


    def __graphtestmode(self):
        """
        Produces an image version of the segmented PPM image overlaying the grid with
        the selected tile size at the test_downsample resolution. Performed using
        Felzenswalb's efficient graph segmentation.
        """

        # Check that the segmentation executable is available
        utility_functions.check_compilation()

        logging.info("== Test mode for graph segmentation ==")
        logging.info("== Producing edge image ==")
        self.__produce_edges()

        logging.info("== Segmentation over the mask ==")
        self.__segment_felzenszwalb()

        # Get information about arguments and image
        image_dims = self.input_slide.slide.dimensions  # (x, y) # UNPACK
        border_pct = self.input_slide.pct_bc / 100
        border_thickness = 2

        # Since we read an numpy array, we need to change BGR -> RGB
        mask = cv2.imread(self.input_slide.img_outpath + "segmented_" + self.input_slide.sample_id + ".ppm")  # (y, x)
        resized_mask = cv2.resize(mask, (image_dims[0]//self.input_slide.test_downsample,
                                        image_dims[1]//self.input_slide.test_downsample))

        # Draw a grid over the image
        x_shift, y_shift = self.input_slide.patch_size, self.input_slide.patch_size
        gcol = [255, 0, 0]
        resized_mask[:, ::y_shift, :] = gcol
        resized_mask[::x_shift, :, :] = gcol

        # Calculate the border percentage
        hpct = round(resized_mask.shape[0] * border_pct)
        wpct = round(resized_mask.shape[1] * border_pct)

        # Draw top and bottom borders
        gcol = [0, 0, 0]
        width_range = range(wpct, resized_mask.shape[1] - wpct)
        resized_mask[hpct:(hpct + border_thickness), width_range, :] = gcol
        resized_mask[(resized_mask.shape[0] - hpct - border_thickness):(resized_mask.shape[0] - hpct), width_range, :] = gcol

        # Draw left and right borders
        height_range = range(hpct, resized_mask.shape[0] - hpct)
        resized_mask[height_range, wpct:(wpct + border_thickness), :] = gcol
        resized_mask[height_range, (resized_mask.shape[1] - wpct - border_thickness):(resized_mask.shape[1] - wpct), :] = gcol

        # Write output image
        outfile = self.input_slide.img_outpath + "test_" + self.input_slide.sample_id + "." + self.input_slide.format
        cv2.imwrite(outfile, resized_mask)


    def __graph(self):
        """Performs Felzenszwalb's efficient graph segmentation to obtain an image mask.

        Returns:
            mask: PIL RGB image.
            bg_color: Numpy array indicating the background color.
        """

        utility_functions.check_compilation()

        logging.info("== Producing edge image ==")
        self.__produce_edges()

        logging.info("== Segmentation over the mask ==")
        self.__segment_felzenszwalb()

        ts = time.time()
        mask = cv2.imread(self.input_slide.img_outpath + "segmented_" + self.input_slide.sample_id + ".ppm")

        # Identify background colors from the mask
        bg_color, bord = utility_functions.bg_color_identifier(mask, self.input_slide.pct_bc, self.input_slide.borders, self.input_slide.corners)

        # If we detect more than one background color, then we replace them all with the first detected background color
        if bord.shape[0] > 1:
            for i in range(1, bord.shape[0]):
                mask[np.where((mask == bord[i]).all(axis=2))] = bg_color

        # Convert to PIL
        mask = Image.fromarray(mask)
        return mask, bg_color


    def __otsu(self):
        """Performs Otsu thresholding to obtain an image mask.

        Returns:
            mask: PIL RGB image.
            bg_color: Numpy array indicating the background color.
        """

        # Get downsampled version of the image
        img, bdl = utility_functions.downsample_image(self.input_slide.slide, self.input_slide.mask_downsample)

        # Information
        logging.debug("Otsu thresholding will be performed with mask downsampling of " + str(self.input_slide.mask_downsample) + "x.")
        logging.debug("SVS level 0 dimensions: " + str(self.input_slide.slide.dimensions))
        logging.debug("Using level " + str(bdl) + " to downsample.")
        logging.debug("Downsampled size: " + str(img.shape[::-1][1:3]))

        # Reverse the image to BGR and convert to grayscale
        img = img[:, :, ::-1]
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Remove noise using a Gaussian filter
        img = cv2.GaussianBlur(img, (5,5), 0)

        # Otsu thresholding and mask generation
        ret, thresh_otsu = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Save mask if requested
        if self.input_slide.save_mask:
            out_filename = self.input_slide.img_outpath + "mask_" + self.input_slide.sample_id + "." + self.input_slide.format
            cv2.imwrite(out_filename, thresh_otsu)

        # Convert to PIL
        mask = Image.fromarray(thresh_otsu)
        bg_color = np.array([255, 255, 255])

        return mask, bg_color


    def __adaptive(self):
        """Performs Adaptive thresholding to obtain an image mask.
        The threshold value is a gaussian-weighted sum of the neighbourhood values minus a constant C
        Here the size of the neighbourhood is equal to 11 and the constant is equal to 2

        Returns:
            mask: PIL RGB image.
            bg_color: Numpy array indicating the background color.
        """

        # Get downsampled version of the image
        img, bdl = utility_functions.downsample_image(self.input_slide.slide, self.input_slide.mask_downsample)

        # Information
        logging.debug("Adaptive thresholding will be performed with mask downsampling of " + str(self.input_slide.mask_downsample) + "x.")
        logging.debug("SVS level 0 dimensions: " + str(self.input_slide.slide.dimensions))
        logging.debug("Using level " + str(bdl) + " to downsample.")
        logging.debug("Downsampled size: " + str(img.shape[::-1][1:3]))

        # Reverse the image to BGR and convert to grayscale
        img = img[:, :, ::-1]
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Adaptive thresholding and mask generation
        thresh_adapt = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        # Save mask if requested
        if self.input_slide.save_mask:
            out_filename = self.input_slide.img_outpath + "mask_" + self.input_slide.sample_id + "." + self.input_slide.format
            cv2.imwrite(out_filename, thresh_adapt)

        # Convert to PIL
        mask = Image.fromarray(thresh_adapt)
        bg_color = np.array([255, 255, 255])

        return mask, bg_color


    # --- Auxiliary functions ---
    def __produce_edges(self):
        """
        Detects edges of an image using cv2's Canny edge detector.
        """

        ts = time.time()

        # Read the image
        img, bdl = utility_functions.downsample_image(self.input_slide.slide, self.input_slide.mask_downsample)

        # Logging info
        logging.debug("Requested " + str(self.input_slide.mask_downsample) + "x downsampling for edge detection.")
        logging.debug("SVS level 0 dimensions:" + str(self.input_slide.slide.dimensions))
        logging.debug("Using level " + str(bdl) + " to downsample.")
        logging.debug("Downsampled size: " + str(img.shape[::-1][1:3]))

        # Run Canny edge detector
        edges = cv2.Canny(img, 100, 200)

        # Save the produced image in PPM format to give to the segmentation algorithm
        edges = Image.fromarray(edges)
        warnings.filterwarnings("ignore")

        edges = edges.convert('RGB')
        edges.save(self.input_slide.img_outpath + "edges_" + self.input_slide.sample_id + ".ppm", 'PPM')
        warnings.filterwarnings("default")
        te = time.time()

        logging.debug("Elapsed time: " + str(round(te-ts, ndigits = 3)) + "s")


    def __segment_felzenszwalb(self):
        '''
        Invokes a shell process to run the graph-based segmentation algorithm
        with a PPM image containing the edges from the Canny detector.

        Raises:
            SystemError: If an error ocurred during segmentation.
        '''

        # Launch segmentation subprocess
        ts = time.time()
        edge_file = self.input_slide.img_outpath + "edges_" + self.input_slide.sample_id + ".ppm"
        ppm_file = self.input_slide.img_outpath + "segmented_" + self.input_slide.sample_id + ".ppm"
        command = ["src/graph_segmentation/segment", str(self.input_slide.sigma), str(self.input_slide.k_const), 
        str(self.input_slide.minimum_segmentsize), edge_file, ppm_file]
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True)
        output, error = process.communicate()
        te = time.time()

        # Logging information
        logging.debug("Elapsed time: " + str(round(te-ts, ndigits = 3)) + "s")

        if error is not None:
            raise RuntimeError(error)


    def __create_tiles(self, mask, bg_color):
        """Create tiles given a PySlide and a mask.

        Arguments:
            mask: PIL Image containing the mask for the slide.
            bg_color: Numpy array indicating the color used for the background in the mask.
        """

        ts = time.time()

        # Create folder for the patches
        if self.input_slide.save_patches:
            self.input_slide._create_tile_folder()

        # Initialize deep zoom generator for the slide
        image_dims = self.input_slide.slide.dimensions
        dzg = deepzoom.DeepZoomGenerator(self.input_slide.slide, tile_size=self.input_slide.patch_size, overlap=0)

        # Find the deep zoom level corresponding to the
        # requested downsampling factor
        dzg_levels = [2**i for i in range(0, dzg.level_count)][::-1]
        dzg_selectedlevel_idx = dzg_levels.index(self.input_slide.output_downsample)
        dzg_selectedlevel_dims = dzg.level_dimensions[dzg_selectedlevel_idx]
        dzg_selectedlevel_maxtilecoords = dzg.level_tiles[dzg_selectedlevel_idx]
        dzg_real_downscaling = np.divide(image_dims, dzg.level_dimensions)[:, 0][dzg_selectedlevel_idx]
        n_tiles = np.prod(dzg_selectedlevel_maxtilecoords)
        digits_padding = len(str(n_tiles))

        # Calculate patch size in the mask
        mask_patch_size = int(np.ceil(self.input_slide.patch_size * (self.input_slide.output_downsample/self.input_slide.mask_downsample)))

        # Deep zoom generator for the mask
        dzgmask = deepzoom.DeepZoomGenerator(openslide.ImageSlide(mask), tile_size=mask_patch_size, overlap=0)
        dzgmask_dims = dzgmask.level_dimensions[dzgmask.level_count - 1]
        dzgmask_maxtilecoords = dzgmask.level_tiles[dzgmask.level_count - 1]
        dzgmask_ntiles = np.prod(dzgmask_maxtilecoords)

        # If needed, generate an image to store tile-crossed output, at the requested tilecross downsample level
        if self.input_slide.save_tilecrossed_image:

            # Get a downsampled numpy array for the image
            tilecrossed_img = utility_functions.downsample_image(self.input_slide.slide,
                self.input_slide.tilecross_downsample, mode="numpy")[0]

            # Calculate patch size in the mask
            tilecross_patchsize = int(np.ceil(self.input_slide.patch_size * (self.input_slide.output_downsample/self.input_slide.tilecross_downsample)))

            # Draw the grid at the scaled patchsize
            x_shift, y_shift = tilecross_patchsize, tilecross_patchsize
            gcol = [255, 0, 0]
            tilecrossed_img[:, ::y_shift, :] = gcol
            tilecrossed_img[::x_shift, :, :] = gcol

            # Convert numpy array to PIL image
            tilecrossed_img = Image.fromarray(tilecrossed_img, mode="RGB")

            # Create object to draw the crosses for each tile
            draw = ImageDraw.Draw(tilecrossed_img)

            # Counters for iterating through the tile-crossed image tiles
            tc_w = 0
            tc_h = 0

        # Debug information
        logging.debug("** Original image information **")
        logging.debug("-Dimensions: " + str(image_dims))

        logging.debug("** Mask information **")
        logging.debug("-Mask downscaling factor: " + str(self.input_slide.mask_downsample))
        logging.debug("-Pixel dimensions: " + str(dzgmask_dims))
        logging.debug("-Calculated patch size: " + str(mask_patch_size))
        logging.debug("-Max tile coordinates: " + str(dzgmask_maxtilecoords))
        logging.debug("-Number of tiles: " + str(dzgmask_ntiles))

        logging.debug("** Output image information **")
        logging.debug("Requested " + str(self.input_slide.output_downsample) + "x downsampling for output.")

        logging.debug("** Properties of selected deep zoom level **")
        logging.debug("-Real downscaling factor: " + str(dzg_real_downscaling))
        logging.debug("-Pixel dimensions: " + str(dzg_selectedlevel_dims))
        logging.debug("-Selected patch size: " + str(self.input_slide.patch_size))
        logging.debug("-Max tile coordinates: " + str(dzg_selectedlevel_maxtilecoords))
        logging.debug("-Number of tiles: " + str(n_tiles))

        logging.info("== Selecting tiles ==")

        if dzgmask_maxtilecoords != dzg_selectedlevel_maxtilecoords:
            logging.info("Rounding error creates extra patches at the side(s) of the image.")
            grid_coord = (min(dzgmask_maxtilecoords[0], dzg_selectedlevel_maxtilecoords[0]),
                min(dzgmask_maxtilecoords[1], dzg_selectedlevel_maxtilecoords[1]))
            logging.info("Ignoring the image border. Maximum tile coordinates: " + str(grid_coord))
            n_tiles = grid_coord[0] * grid_coord[1]
        else:
            grid_coord = dzg_selectedlevel_maxtilecoords

        # Counters
        preds = [0] * n_tiles
        row, col, i = 0, 0, 0
        tile_names = []
        tile_dims_w = []
        tile_dims_h = []
        tile_rows = []
        tile_cols = []

        # Evaluate tiles using the selector function
        while row < grid_coord[1]:

            # Extract the tile from the mask (the last level is used
            # since the mask is already rescaled)
            mask_tile = dzgmask.get_tile(dzgmask.level_count - 1, (col, row))

            # Tile converted to BGR
            mask_tile = np.array(mask_tile)

            # Predict if the tile will be kept (1) or not (0)
            preds[i] = utility_functions.selector(mask_tile, self.input_slide.thres, bg_color, self.input_slide.method)

            # Save patches if requested
            if self.input_slide.save_patches:
                tile = dzg.get_tile(dzg_selectedlevel_idx, (col, row))

                # If we need square patches only, we set the prediction to zero if the tile is not square
                if not self.input_slide.save_nonsquare:
                    if tile.size[0] != tile.size[1]:
                        preds[i] = 0

                # Prepare metadata
                tile_names.append(self.input_slide.sample_id + "_" + str(i).zfill(digits_padding))
                tile_dims_w.append(tile.size[0])
                tile_dims_h.append(tile.size[1])
                tile_rows.append(row)
                tile_cols.append(col)

                # Save tile
                imgtile_out = self.input_slide.tile_folder + tile_names[i] + "." + self.input_slide.format
                if self.input_slide.save_blank:
                    tile.save(imgtile_out)
                else:
                    if preds[i] == 1:
                        tile.save(imgtile_out)

            # Draw cross over corresponding patch section on tilecrossed image
            if self.input_slide.save_tilecrossed_image:
                start_w = col * (tilecross_patchsize)
                start_h = row * (tilecross_patchsize)

                # If we reach the edge of the image, we only can draw until the edge pixel
                if (start_w + tilecross_patchsize) >= tilecrossed_img.size[0]:
                    cl_w = tilecrossed_img.size[0] - start_w
                else:
                    cl_w = tilecross_patchsize

                if (start_h + tilecross_patchsize) >= tilecrossed_img.size[1]:
                    cl_h = tilecrossed_img.size[1] - start_h
                else:
                    cl_h = tilecross_patchsize

                # Draw the cross only if the tile has to be kept
                if preds[i] == 1:

                    # From top left to bottom right
                    draw.line([(start_w, start_h), (start_w + cl_w, start_h + cl_h)], fill=(0, 0, 255), width=3)

                    # From bottom left to top right
                    draw.line([(start_w, start_h + cl_h), (start_w + cl_w, start_h)], fill=(0, 0, 255), width=3)

                # Jump to the next tilecross tile
                tc_w = tc_w + tilecross_patchsize + 1

            # Jump to the next column tile
            col += 1

            # If we reach the right edge of the image, jump to the next row
            if col == grid_coord[0]:
                col = 0
                row += 1

                if self.input_slide.save_tilecrossed_image:
                    tc_w = 0
                    tc_h = tc_h + tilecross_patchsize + 1

            # Increase counter for metadata
            i += 1

        # Saving tilecrossed image
        if self.input_slide.save_tilecrossed_image:
            tilecrossed_outpath = self.input_slide.img_outpath + "/tilecrossed_" + self.input_slide.sample_id + "." + self.input_slide.format
            tilecrossed_img.save(tilecrossed_outpath)

        # Save predictions for each tile
        if self.input_slide.save_patches:
            patch_results = []
            patch_results.extend(list(zip(tile_names, tile_dims_w, tile_dims_h, preds, tile_rows, tile_cols)))
            patch_results_df = pd.DataFrame.from_records(patch_results, columns=["Tile", "Width", "Height", "Keep", "Row", "Column"])
            patch_results_df.to_csv(self.input_slide.img_outpath + "tile_selection.tsv", index=False, sep="\t")

        # Finishing
        te = time.time()
        logging.debug("Elapsed time: " + str(round(te - ts, ndigits = 3)) + "s")

        if self.input_slide.save_blank:
            logging.debug("Selected " + str(len(preds)) + " tiles")
        else:
            logging.debug("Selected " + str(sum(preds)) + " tiles")