<h1 align="center">
<p>PyHIST: An Histological Image Segmentation Tool
</h1>

[About PyHIST](#about) | [Setup](#setup) | [Quickstart](#quickstart) | [Tutorial](#tutorial) | [References](#references)

## About PyHIST<a name="about"></a>

A semi-automatic pipeline to segment tissue slices from the background in high resolution whole-slde histopathological images. Furthermore, it extracts patches of tissue segments from the full resolution image. 

Whole slide histological images are very large in terms of size, making it difficult for computational pipelines to process them as single units, thus, they have to be divided into patches. Moreover, a significant portion of each image is background, which should be excluded from downstream analyses. 
    
In order to efficiently segment tissue content from each image, the pipeline utilizes a Canny edge detector and a graph-based segmentation algorithm. A lower resolution version of the image, extracted from the whole slide image file, is segmented. The background is defined as the segments that can be found at the borders or corners of the image. Finally, patches are extracted from the full size image ,while the corresponding patches are checked in the segmented image. Patches with a "tissue content" greater than a threshold value are selected.

Moreover, the pipeline can function in test mode. This could assist the user in setting the appropriate parameters for the pipeline. In test mode, the segmented version of the input image with scales indicating the number of rows and columns will be produced. In that image the background should be separate from the tissue pieces for the pipeline to work properly. 



## Setup<a name="setup"></a>
Clone the repository and navigate to it:

```shell
git clone https://github.com/manuel-munoz-aguirre/HistologySegment.git
cd HistologySegment
```
 downloading the repository, move inside the repository folder:

### PyHIST Docker image
After downloading the repository, move inside the repository folder:

```shell
cd HistologySegment
```

To build the docker image run the following command:

```shell
docker build -f docker/Dockerfile -t histologysegment .
```

### Installation

Python 3

| Required python Libraries |
|:-------------------------:|
| Numpy                     |
| Pandas                    |
| OpenCV                    |
| OpenSlide                 |
| Pillow                    |
| Matplotlib                | 


## Quickstart<a name="quickstart"></a>
### Using the docker image

Once the image is built, to execute HistologySegment with docker, interactive session is required.

Because the image is used in a docker container which has its own file system, to use the program with local files, a host data volume needs to be mounted.


```shell
docker run -u USERID:GROUPID -it -v $PWD:$PWD histologysegment bash
./segment_hist --help # check the help page
./segment_hist -k 1000 -m 1000 -l 2 -d 1024 -n 50 -pfxet 0.1 path/to/input/file # run the pipeline
mv segment_hist_output/ mounted/folder/ # move the output in the local system
exit # exit the interactive session
```
The '-v' option mounts the current working directory and all child folders inside the container to the same path (host_path:container_path).

### Using PyHIST
TODO

## Tutorial <a name="tutorial"></a>
TODO



<!-- ## Examples -->

<!-- python segment_hist.py --content-threshold 0.05 --sigma 0.7 --patch-size 64 --mask-downsample 16 --output-downsample 16 --tilecross-downsample 64  --verbose --save-tilecrossed-image test_resources/GTEX-1117F-0125.svs -->

<!-- Keep segmented image, save patches, produce a thumbnail with marked the selected patches, use a content threshold of 0.1 for patch selection. -->
    
<!-- ``` -->
<!-- segment_hist -pfxt 0.1 INPUT_FILE -->

<!-- segment_hist -p -f -x -t 0.1 INPUT_FILE -->
<!-- ```     -->
    
<!-- Do not save patches, produce thumbnail, use different than the default values for k and m parameters. -->

<!-- ``` -->
<!-- segment_hist -xk 10000 -m 1000 INPUT_FILE -->
<!-- ``` -->
<!-- Do not save patches, produce thumbnail, use a content threshold of 0.1 for patch selection, for background identification use bottom left and top right corners. -->
    
<!-- ``` -->
<!-- segment_hist -xt 0.1 --borders 0000 --corners 0101 INPUT_FILE -->
<!-- ``` -->

<!-- Function in test mode, use different than the default values for k and m parameters. -->
    
<!-- ``` -->
<!-- segment_hist --test -k 1000 -m 1000 INPUT_FILE -->
<!-- ``` -->

<!-- Show the help page. -->

<!-- ``` -->
<!-- segment_hist -h -->
<!-- ``` -->

## References<a name="references"></a>

Felzenszwalb, P.F., & Huttenlocher, D.P. (2004). Efficient Graph-Based Image Segmentation. International Journal of Computer Vision, 59, 167-181.
