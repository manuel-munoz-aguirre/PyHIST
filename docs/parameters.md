# Parameter documentation

PyHist usage: `pyhist.py [parameters] input_image`

#### _PyHist parameters_
* [Help](#help)
* [Test mode](#test)
* [Input image](#input)
* [Output](#output)
* [Output Format](#format)
* [Patch size](#p_size)
* [Save a tilecrossed image](#save_tc)
* [Save edges](#save_e)
* [Save mask](#save_m)
* [Save patces](#save_p)
* [Output downsample](#down_o)
* [Mask downsample](#down_m)
* [Tilecrossed image downsample](#down_tc)
* [Borders](#borders)
* [Corners](#corners)
* [Percentage of the image - background definition](#perc)
* [K constant](#k_const)
* [Minimum segment size ](#min_ssize)
* [Sigma factor](#sigma)
* [Content threshold](#thres)
* [Verbose](#verbose)

---

## Help<a name="help"></a>
`-h, --help`

Print the help page and exit.

## Test mode<a name="test"></a>
`--test-mode`

Function in test mode. This will produce a segmented image of the
input with an overlayed grid that indicates the division of the image
into patches. Moreover, the area of the image that is taken under 
consideration for the background identification will also be
illustrated. Test mode is extremely useful for tuning the different
parameters of the pipeline, as well as for troubleshooting.

## Input image<a name="input"></a>
`input_image`

The input image to be segmented. It has to be an svs file.

## Output<a name="output"></a>
`--output OUTPUT`

Path of a folder, in which the output is going to be saved. The 
default is `./output/`.

## Output Format<a name="format"></a>
`--format FORMAT`

A character string indicating the format of the produced patches. It
could take the values png or jpg. The default value is png.

## Patch size<a name="p_size"></a>
`--patch-size PATCH_SIZE`

The desired size of the patches produced by the pipeline. The output patches will be square.
Hence, PATCH_SIZE should be an integer indicating the number of pixels of the width (or height)
of each patch. A value of D will produce patches of size D x D. The default value is 512.

## Save a tilecrossed image<a name="save_tc"></a>
`--save-tilecrossed-image`

Produce a downsized version of the input image, in which the poduced patches are indicated with 
a red grid. The selected patches, that passed the "tissue content" filtering are highlighted 
with an overlayed blue cross. By default, PyHist is not going to 
create this image.

## Save edges<a name="save_e"></a>
`--save-edges`

Keep the image produced by the Canny edge detector. This is a downsized version of the input 
image that highlights the edges of objects inside the image. By default PyHist will not keep 
this image.


## Save mask<a name="save_m"></a>
`--save-mask`

Keep the mask image. This is a downsized version of the input image containing the result of the
segmentation process. Each segment is indicated with a discrete colour. By default PyHist will 
not keep this image.

## Save patches<a name="save_p"></a>
`--save-patches`

Save the patches of the original image that passed the "tissue content" filtering. By default
PyHist will not save them.

## Output  downsample<a name="down_o"></a>
`--output-downsample OUTPUT_DOWNSAMPLE`

This is an integer indicating the downsampling of the original image
before dividing it into patches.
It must be a power of 2. The default value is 16.

## Mask downsample<a name="down_m"></a>
`--mask-downsample MASK_DOWNSAMPLE`

This is an integer indicating the downsampling of the input before
the generation of mask. It must be a power of 2. The default value is
16.

## Tilecrossed image downsample<a name="down_tc"></a>
`--tilecross-downsample TILECROSS_DOWNSAMPLE`

This is an integer indicating the downsampling of the tile-crossed
image. It must be a power of 2. The default value is 16.

## Borders<a name="borders"></a>
`--borders 1111`

A four digit binary number. Each digit represents a border of the 
image in the following order: left, bottom, right, top. If the digit 
is 1, then the corresponding border will be taken into account to 
define background. For instance, with 1010 the algorithm will look at
the left and right borders of the segmented image, in a window of 
width defined by the PERCENTAGE_BC  argument, and every segment 
identified will be set as background. This argument is mutually 
exclusive with --corners. If --borders is set to be different from
0000, then --corners must be 0000. The default value is 1111.

## Corners<a name="corners"></a>
`--corners 0000`

A four digit binary number. Each digit represents a corner of the image in the
following order: top left, bottom left, bottom right, top right. If the
digit is equal to 1, then the corresponding corner will be taken
into account to define background. For instance, with 0101, the
bottom left and top right corners of the segmented image will be considered,
with a window of size given by the PERCENTAGE_BC argument, 
and every segment identified will be set as background. This argument is
mutually exclusive with --borders. If --corners is set to be different from
0000, then --borders must be 0000. The default value is 0000.

## Percentage of the image - background definition<a name="perc"></a>
`--percentage-bc PERCENTAGE_BC`

This is an Interger ranging from 0 to 100. Indicates the percentage
(applied to width and height) of the image that will be taken under
consideration for the definition of the background.

## K constant<a name="k_const"></a>
`--k-const K_CONST`

An integer constant required by the segmentation algorithm.
Needed for the threshold function. The threshold function controls the
degree to which the difference between two segments must be greater than
their internal differences in order for them not to be merged. Lower values
result in finer segmentation. Larger images require higher values.
The default value is 10000.

## Minimum segment size<a name="min_ssize"></a>
`--minimum_segmentsize MINIMUM_SEGMENTSIZE`

An integer required by the segmentation algorithm.
It is the minimum segment size enforced by post-processing.
Larger images require higher values.
The default value is 10000.

## Sigma factor<a name="sigma"></a>
`--sigma SIGMA`

A parameter required by the segmentation algorithm.
It is used to smooth the input image before segmenting it.
The default value is 0.5.

## Content threshold<a name="thres"></a>
`--content-threshold CONTENT_THRESHOLD`

A threshold parameter ranging from 0 to 1. It indicates the
proportion of a patch's content that should not be covered by background
in order to be selected. The default value is 0.5.

## Verbose<a name="verbose"></a>
`--verbose`

Print status messages at each step of the pipeline. By default, PyHist
will not do this.
