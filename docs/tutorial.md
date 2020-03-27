# How does PyHIST work?
PyHIST works with SVS files. From an input SVS image (1), it first produces a version of the image that highlights tissue edges using a Canny edge detector (2). Then, a [graph segmentation](http://people.cs.uchicago.edu/~pff/papers/seg-ijcv.pdf) algorithm is executed over it in order to generate a mask of the image regions with tissue content, i.e. differentiating the background (contiguous color region) from the foreground (different colors) (3). Finally, the original image is divided into tiles and these are written to disk together with a log file indicating which tile coordinates (0-based indexing) contain tissue content.

<div align="center">
<img src="https://raw.githubusercontent.com/manuel-munoz-aguirre/PyHIST/master/docs/resources/how_pyhist_works.png" alt="how_pyhist_works"></img>
</div>

With PyHIST, images can be downsampled at factors that are powers of 2 at different stages of the process: when the mask is downsampled, the segmentation process is faster since it is executed at a lower resolution. The overview image can also be downsampled: since it is used as a sanity check of the segmentation process, it is usually not necessary to keep a large version. Finally, the output image can also be downsampled: depending on the application, it may be sufficient to work with a lower resolution version of the original image. Tile extraction can also be done over the downsampled version of the image. 

<div align="center">
<img src="https://raw.githubusercontent.com/manuel-munoz-aguirre/PyHIST/master/docs/resources/downsamples.png" alt="downsamples"></img>
</div>


# Creating tiles from an histological image
We will work with a skin image from the [GTEx Histological Images resource](https://brd.nci.nih.gov/brd/image-search/search_specimen/). Download the sample with: 

	curl 'https://brd.nci.nih.gov/brd/imagedownload/GTEX-1117F-0126' --output 'GTEX-1117F-0126.svs'

If you have `ImageMagick` installed, the image properties can be viewed with the `identify` command. Level 0 contains the highest resolution for the image, while levels 2 and 3 are downsamples of 4x and 16x respectively. PyHIST will perform downsampling (if requested) with the most appropriate image level.
	
	identify GTEX-1117F-0126.svs

	> GTEX-1117F-0126.svs[0] TIFF 47807x38653 47807x38653+0+0 8-bit sRGB 328.3MB 0.000u 0:00.000
	> GTEX-1117F-0126.svs[1] TIFF 949x768 949x768+0+0 8-bit sRGB 328.3MB 0.000u 0:00.000
	> GTEX-1117F-0126.svs[2] TIFF 11951x9663 11951x9663+0+0 8-bit sRGB 328.3MB 0.000u 0:00.000
	> GTEX-1117F-0126.svs[3] TIFF 2987x2415 2987x2415+0+0 8-bit sRGB 328.3MB 0.000u 0:00.000
	> GTEX-1117F-0126.svs[4] TIFF 1600x629 1600x629+0+0 8-bit sRGB 328.3MB 0.000u 0:00.000

Let's assume that we want to extract tiles of size 64x64 at a downsampled resolution of 16x. PyHIST has a test mode that allows us to verify the image masking, as well as how the image tiles will look like at the requested resolution. By default, output will be saved in a folder with the same name as the input image:

	python pyhist.py --patch-size 64 --output-downsample 16 --test-mode GTEX-1117F-0126.svs
	eog output/GTEX-1117F-0126/test_GTEX-1117F-0126.png

<a name="testimage">
<div align="center">
<img src="https://raw.githubusercontent.com/manuel-munoz-aguirre/PyHIST/master/docs/resources/test_GTEX-1117F-0126.png" alt="GTEx_mask_test"></img>
</div>
</a>
<br>

The faint black border that is not part of the grid is an aid for the segmentation and it is explained in the [parameter tuning](#parametertuning) section. Once we verify the tiling and masking, we proceed to extract the tiles using the `--save-patches` flag. To save an overview image of the tiles that were selected, add the `--save-tilecrossed-image` flag. To see details of the mask generation and tile extraction, use the `--verbose` flag.

	python pyhist.py --patch-size 64 \
	--output-downsample 16 \
	--save-patches \
	--save-tilecrossed-image \
	--verbose \
	GTEX-1117F-0126.svs 


```shell
Requested 16x downsampling for edge detection.
SVS level 0 dimensions: (47807, 38653)
Using level 2 to downsample.
Downsampled size: (2987, 2415)
Elapsed time: 0.8531272411346436

== Step 2: Segmentation over the mask ==
Elapsed time: 3.970844030380249

== Step 3: Selecting tiles ==
Original image dimensions: (47807, 38653)

Mask information: 
-Mask downscaling factor: 16
-Pixel dimensions: (2987, 2415)
-Calculated patch size: 64
-Max tile coordinates: (47, 38)
-Number of tiles: 1786

Output image information: 
Requested 16x downsampling for output.
Properties of selected deep zoom level:
-Real downscaling factor: 15.999665327978581
-Pixel dimensions: (2988, 2416)
-Selected patch size: 64
-Max tile coordinates: (47, 38)
-Number of tiles: 1786

Selecting patches...
Elapsed time: 19.665995597839355
```

The generated overview image `output/GTEX-1117F-0126/tilecrossed_GTEX-1117F-0126.png` is below. The blue crosses mark the tiles that are selected as containing tissue content.
<div align="center">
<img src="https://raw.githubusercontent.com/manuel-munoz-aguirre/PyHIST/master/docs/resources/tilecrossed_GTEX-1117F-0126.png" alt="GTEx_tilecrossed"></img>
</div>

Depending on the application, we may want to be more (or less) strict on the amount of tissue we want to keep. To control this, we can use the `--content-threshold` flag, which is the minimal amount of tissue required (bounded to [0, 1] where 0 is no tissue content, and 1 is completely filled with tissue). To keep the edges of the tissue fragments in this sample skin image, we can set this flag as:

```shell
python pyhist.py --patch-size 64 \
	--content-threshold 0.05 \
	--output-downsample 16 \
	--save-patches \
	--save-tilecrossed-image \
	--verbose GTEX-1117F-0126.svs
```
[Explain tile saving formats]

# Random patch sampling<a name="randomsapling"></a>
It is also to randomly sample a given number of tiles of a given size from the WSI at any downscaling factor. For example, to extract 200 tiles at random from the native WSI resolution:
```shell
python pyhist.py --sampling \
	--npatches 200 \
	--output-downsample 1 \
	GTEX-1117F-0126.svs
```

# Parameter tuning<a name="parametertuning"></a>
PyHIST has some auxiliary tuning parameters that can be modified to change how the segmentation is performed. Here we show a the effect of tweaking an important parameter: *borders*. PyHIST checks either: 
a) the four borders (default) or b) the four corners of the image to aid in the determination of the background color. For example, on the [test mode image](#testimage) shown above, everything that is outside the region enclosed by the black square is defined to be as background color. However, sometimes, there is tissue content in the border, which leads to an incorrect segmentation. In those case, we simply override checking the offending sides with the `--borders` parameter, which takes a four digit string as an argument indicating which sides need to be considered, in order of left, bottom, right, top. In the case above, to override the check for the top and right borders, we would call PyHIST with `--borders 1100`:

![borders_argument](resources/borders_argument.png)

The same logic applies for `--corners` parameter. The checking of borders/corners is mutually exclusive - only one can be set at a time. By default, determination of background is done using the borders. For the complete list of parameters, refer to the [parameters](parameters.md) page.
