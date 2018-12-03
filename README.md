# HistologySegment

##Descritpion

A semi-automatic pipeline to segment tissue slices from the background in high resolution whole-slde histopathological images. Furthermore, it extracts patches of tissue segments from the full resolution image. 

Whole slide histological images are very large in terms of size, making it difficult for computational pipelines to process them as single units, thus, they have to be divided into patches. Moreover, a significant portion of each image is background, which should be excluded from downstream analyses. 
    
In order to efficiently segment tissue content from each image, the pipeline utilizes a Canny edge detector and a graph-based segmentation algorithm. A lower resolution version of the image, extracted from the whole slide image file, is segmented. The background is defined as the segments that can be found at the borders or corners of the image. Finally, patches are extracted from the full size image ,while the corresponding patches are checked in the segmented image. Patches with a "tissue content" greater than a threshold value are selected.

Moreover, the pipeline can function in test mode. This could assist the user in setting the appropriate parameters for the pipeline. In test mode, the segmented version of the input image with scales indicating the number of rows and columns will be produced. In that image the background should be separate from the tissue pieces for the pipeline to work properly. 

## Dependencies
Bash

Python 3

| Required python Libraries |
|:-------------------------:|
| Numpy                     |
| Pandas                    |
| OpenCV                    |
| OpenSlide                 |
| Pillow                    |
| Matplotlib                | 


##Examples


Keep segmented image, save patches, produce a thumbnail with marked the selected patches, use a content threshold of 0.1 for patch selection.
    
```bash
segment_hist -pfxt 0.1 -i INPUT_FILE

segment_hist -p -f -x -t 0.1 -i INPUT_FILE
```    
    
Do not save patches, produce thumbnail, use different than the default values for k and m parameters.

```bash
segment_hist -xk 10000 -m 1000 -i INPUT_FILE
```
Do not save patches, produce thumbnail, use a content threshold of 0.1 for patch selection, for background identification use bottom left and top right corners.
    
```bash
segment_hist -xt 0.1 -b 0000 -c 0101 -i INPUT_FILE
```

Function in test mode, use different than the default values for k and m parameters.
    
```bash
segment_hist test -k 1000 -m 1000 -i INPUT_FILE
```
    
## REFERENCES

Felzenszwalb, P.F., & Huttenlocher, D.P. (2004). Efficient Graph-Based Image Segmentation. International Journal of Computer Vision, 59, 167-181.
