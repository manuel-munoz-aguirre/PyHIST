# Parameter documentation

PyHIST usage: `pyhist.py [parameters] input_image`

### _PyHIST parameters_
* [Input image](#input)
* [Help](#help)
* [Test mode](#test)
* [Verbose](#verbose)
* [Sampling](#sampling)
* [Number of sampled tiles](#npatches)
* [Output](#output)
* [Output Format](#format)
* [Tile size](#p_size)
* [Save a tilecrossed image](#save_tc)
* [Save edges](#save_e)
* [Save mask](#save_m)
* [Save tiles](#save_p)
* [Exclude background tiles](#exclude_bg)
* [Save nonsquare tiles](#save_nonsquare)
* [Output downsample](#down_o)
* [Mask downsample](#down_m)
* [Tilecrossed image downsample](#down_tc)
* [Test image downsample](#down_test)
* [Borders](#borders)
* [Corners](#corners)
* [Percentage of the image to define the background](#perc)
* [K constant](#k_const)
* [Minimum segment size](#min_ssize)
* [Sigma factor](#sigma)
* [Content threshold](#thres)

---

## Positional

### Input image<a name="input"></a>
`input_image`

The input SVS image to be segmented.

## Optional

### Help<a name="help"></a>
`-h, --help`

Print the help page and exit.


## Execution

### Test mode<a name="test"></a>
`--test-mode`

Test mode will produce a segmented image of the input with an overlaid grid that shows how the image will be divided at the selected tile size. The area of the image that is used to identify the background will be indicated by a black border. When running in test mode, PyHIST will also keep the output of edge detection and segmentation processes. Test mode is useful for tuning different pipeline parameters and looking at how the tile partition will be before actually saving the tiles. 


### Verbose<a name="verbose"></a>
`--verbose`

Print status messages at each step of the pipeline. By default, PyHIST will not do this.

## Random tile sampling

### Sampling<a name="sampling"></a>
`--sampling`

Function in random patch sampling mode. This will output a random set of the produced patches. By default, PyHIST will not operate in sampling mode.

### Number of sampled tiles<a name="npatches"></a>
`--npatches NPATCHES`

This is an integer indicating the number of patches randomly sampled on sampling mode. The default value is 100.

## Output

### Output<a name="output"></a>
`--output OUTPUT`

Output path. `OUTPUT` is a folder in which the output is going to be saved. If the folder does not exist, it will be created. The default value is `output/`.

### Output Format<a name="format"></a>
`--format FORMAT`

A character string indicating the format (either `png` or `jpg`) of the produced patches. The default value is png.

### Tile size<a name="p_size"></a>
`--patch-size PATCH_SIZE`

The desired size of the patches produced by the pipeline. The output patches will be square. `PATCH_SIZE` should be an integer indicating the number of pixels of the width/height of each patch. A value of P will produce patches of size P x P. The default value is 512.

### Save a tilecrossed image<a name="save_tc"></a>
`--save-tilecrossed-image`

Produce a downsampled version of the input image, in which the tiling grid is drawn in red and the selected tiles that passed the "tissue content" filtering are marked with a blue cross. By default, PyHIST will not create this image.

### Save edges<a name="save_e"></a>
`--save-edges`

Keep the image produced by the Canny edge detector. This is a downsampled version of the input image that highlights the edges of objects inside the image. By default PyHIST will not keep  this image.


### Save mask<a name="save_m"></a>
`--save-mask`

Keep the mask image. This is a downscaled version of the input image containing the result of the segmentation process. Each segment is indicated with a different colour. By default PyHIST will not keep this image.

### Save tiles<a name="save_p"></a>
`--save-patches`

Save all the produced tiles from the at the selected output resolution (see `--output-downsample`). By default PyHIST will not save the tiles.

### Exclude background tiles<a name="exclude_bg"></a>
`--exclude-blank`

By default, all tiles from the image will be saved. If enabled, only foreground patches (tissue) will be saved. 

### Save nonsquare tiles<a name="save_nonsquare"></a>
`--save-nonsquare`
By default, only square tiles are saved, discarding the regions towards the edges of the WSI that do not fit a complete tile. If this flag is enabled, these non-square tiles will be saved as well. The default is False.


## Downsampling

### Output downsample<a name="down_o"></a>
`--output-downsample OUTPUT_DOWNSAMPLE`

`OUTPUT_DOWNSAMPLE` is an integer indicating the downsampling factor for the original image before dividing it into tiles. It must be a power of 2. The default value is 16.

### Mask downsample<a name="down_m"></a>
`--mask-downsample MASK_DOWNSAMPLE`

`MASK_DOWNSAMPLE` is an integer indicating the downsampling factor of the input before edge detection and generation of the mask. It must be a power of 2. The default value is 16.

### Tilecrossed image downsample<a name="down_tc"></a>
`--tilecross-downsample TILECROSS_DOWNSAMPLE`

`TILECROSS_DOWNSAMPLE` is an integer indicating the downsampling factor of the tile-crossed image. It must be a power of 2. The default value is 16.

### Test image downsample<a name="down_test"></a>
`--test-downsample TEST_DOWNSAMPLE`

`TEST_DOWNSAMPLE` is an integer indicating the downsampling factor of the image produced when functioning in test mode. It must be a power of 2. The default value is 16.


## Segmentation

### Borders<a name="borders"></a>
`--borders 1111`

A four digit binary number. Each digit represents a border of the image in the following order: left, bottom, right, top. If a digit is 1, then the corresponding border will be taken into account to define background. For instance, with 1010, PyHIST will look at the left and right borders of the segmented image, in a window of width defined by the `PERCENTAGE_BC` argument, and every segment identified in that window will be set as background. This argument is mutually exclusive with `--corners`. If `--borders` is set to be different from 0000, then `--corners` must be 0000. The default value is 1111.

### Corners<a name="corners"></a>
`--corners 0000`

A four digit binary number. Each digit represents a corner of the image in the following order: top left, bottom left, bottom right, top right. If a digit is equal to 1, then the corresponding corner will be taken into account to define background. For instance, with 0101, the bottom left and top right corners of the segmented image will be considered, in a window of size given by the `PERCENTAGE_BC` argument, and every segment identified will be set as background. This argument is mutually exclusive with `--borders`. If `--corners` is set to be different from 0000, then `--borders` must be 0000. The default value is 0000.

### Percentage of the image - background definition<a name="perc"></a>
`--percentage-bc PERCENTAGE_BC`

`PERCENTAGE_BC` is an interger ranging from 0 to 100, indicating the percentage (applied to width and height) of the image that will be taken under consideration for the definition of the background. The default value is 5.

### K constant<a name="k_const"></a>
`--k-const K_CONST`

`K_CONST` is an integer constant required by the segmentation algorithm that controls the degree to which the difference between two segments must be greater than their internal differences in order for them not to be merged. Lower values result in finer segmentation. Larger images require higher values. If the downsampling factor for the mask is adjusted, this parameter might need to adjusted as well. The default value is 10000.

### Minimum segment size<a name="min_ssize"></a>
`--minimum_segmentsize MINIMUM_SEGMENTSIZE`

`MINIMUM_SEGMENTSIZE` is an integer required by the segmentation algorithm. It is the minimum segment size enforced by post-processing. Larger images require higher values. If the downsampling factor for the mask is adjusted, this parameter might need to adjusted as well. The default value is 10000.

### Sigma factor<a name="sigma"></a>
`--sigma SIGMA`

`SIGMA` is a value required by the segmentation algorithm. It is used to smooth the input image before segmenting it. The default value is 0.5.

### Content threshold<a name="thres"></a>
`--content-threshold CONTENT_THRESHOLD`

`CONTENT_THRESHOLD` can range between 0 and 1, and indicates the proportion of the tile area that should be foreground in order to select the tile. The default value is 0.5.

