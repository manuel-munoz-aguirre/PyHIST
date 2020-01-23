<div align="center">
<img src="https://raw.githubusercontent.com/manuel-munoz-aguirre/PyHIST/master/docs/resources/pyhist293px.png" alt="logo"></img>
</div>

<h1 align="center">
<p>PyHIST: A Histological Image Segmentation Tool
<br>
<a href="https://github.com/manuel-munoz-aguirre/PyHIST/blob/master/LICENSE">
<img alt="GitHub" src="https://img.shields.io/badge/License-GPLv3-blue.svg">
</a>

<a href='https://pyhist.readthedocs.io/en/latest/?badge=latest'>
<img src='https://readthedocs.org/projects/pyhist/badge/?version=latest' alt='Documentation Status' />
</a>
</h1>

[About PyHIST](#about) | [Setup](#setup) | [Quickstart](#quickstart) | [Tutorial](#tutorial) | [References](#references)

## About PyHIST<a name="about"></a>

PyHIST is a **H**istological **I**mage **S**egmentation **T**ool. It is a semi-automatic pipeline to segment tissue slices from the background in high resolution whole-slde histopathological images. Furthermore, it extracts patches of tissue segments from the full resolution image. 

Whole slide histological images are very large in terms of size, making it difficult for computational pipelines to process them as single units, thus, they have to be divided into patches. Moreover, a significant portion of each image is background, which should be excluded from downstream analyses. 
    
In order to efficiently segment tissue content from each image, the pipeline utilizes a Canny edge detector and a graph-based segmentation algorithm. A lower resolution version of the image, extracted from the whole slide image file, is segmented. The background is defined as the segments that can be found at the borders or corners of the image. Finally, patches are extracted from the full size image ,while the corresponding patches are checked in the segmented image. Patches with a "tissue content" greater than a threshold value are selected.

Moreover, the pipeline can function in test mode. This could assist the user in setting the appropriate parameters for the pipeline. In test mode, the segmented version of the input image with scales indicating the number of rows and columns will be produced. In that image the background should be separate from the tissue pieces for the pipeline to work properly. 



## Setup<a name="setup"></a>
The Docker image described in the section below contains all the necessary dependencies to run PyHIST. To install locally, skip to the [installation](#installation) section.

### PyHIST Docker image
The public docker image for PyHIST can be downloaded from the Docker Hub:
```shell
docker pull [TO DO]
```

After downloading it, you can skip directly to [Quickstart: Using the Docker image](#usedocker). Alternatively, you can build the Docker image on your own by using the Dockerfile in this repository. Clone the respository and move into the folder:
```shell
git clone https://github.com/manuel-munoz-aguirre/PyHIST.git
cd PyHIST
```

Build the docker image with the following command:
```shell
docker build -f docker/Dockerfile -t pyhist .
```

### Installation<a name="installation"></a>
Clone the respository and move into the folder:
```shell
git clone https://github.com/manuel-munoz-aguirre/PyHIST.git
cd PyHIST
```

PyHIST has the following dependencies:
* Python (>3.6):
  * openslide, pandas, numpy, PIL, cv2
* Other:
  * openslide-tools, libgl1-mesa-glx, pixman==0.36.0

A `conda` environment with all the necessary Python dependencies can be created with:
```
conda env create -f conda/environment.yml
```

Compile the segmentation tool:
```
cd src/graph_segmentation/
make
```

## Quickstart<a name="quickstart"></a>
### Using the Docker image<a name="usedocker"></a>
PyHIST can be directly executed using Docker:
```shell
docker run pyhist --help
```

To mount a local folder `/path_with/images/` mapping to the folder `/pyhist/images/` inside the container, use the `-v` flag specifying the absolute path of the local folder. 
```shell
docker run -v /path_with/images/:/pyhist/images/ pyhist [args]
```

Optionally, if you want to ensure that all the generated output files are written with permissions belonging to the current host user (instead of `root`, which is Docker's default), specify the username and group with the `-u` flag (retrieval of both can be automated with `id` ), as well mapping the `passwd` file with a second `-v` flag: 
```shell
docker run -v /path_with/images/:/pyhist/images/ -u $(id -u):$(id -g) -v /etc/passwd:/etc/passwd pyhist [args]
```

A working example to process an image called `test.svs` located inside `/path_with/images/`:
```shell
docker run -v /path_with/images/:/pyhist/images/ -u $(id -u):$(id -g) -v /etc/passwd:/etc/passwd pyhist --save-tilecrossed-image --output images/ images/test.svs
```

### Using PyHIST
PyHIST can be directly executed as a script. 
To see all available options:
```
python pyhist.py --help
```

A working example to process an image called `test.svs` located inside `/path_with/images/`:
```
python pyhist.py --content-threshold 0.05 --sigma 0.7 --patch-size 64 --mask-downsample 16 --output-downsample 16 --tilecross-downsample 64 --verbose --save-tilecrossed-image /path_with/images/test.svs
```

## Tutorial <a name="tutorial"></a>
PyHIST's [tutorial](https://pyhist.readthedocs.io) contains documentation explaining all available arguments and processing modes, as well as examples to perform histological image segmentation, patch sampling, and explanations of the inner workings of the segmentation pipeline.


## References<a name="references"></a>
Felzenszwalb, P.F., & Huttenlocher, D.P. (2004). Efficient Graph-Based Image Segmentation. International Journal of Computer Vision, 59, 167-181.
