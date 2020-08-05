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

[About PyHIST](#about) | [Setup](#setup) | [Quickstart](#quickstart) | [Documentation](#documentation) | [References](#references)

## About PyHIST<a name="about"></a>

PyHIST is a Histological Image Segmentation Tool: a lightweight semi-automatic pipeline to extract tiles from SVS histopathology whole image slides (with experimental support for [other formats](#documentation)). It is intended to be an easy-to-use tool to preprocess histological image data for usage in machine learning tasks. It generates a mask for the foreground (tissue slices), and extract tiles from the full resolution image.

<div align="center">
<img src="https://raw.githubusercontent.com/manuel-munoz-aguirre/PyHIST/master/docs/resources/how_pyhist_works.png" alt="logo" width=600></img>
</div>

## Setup<a name="setup"></a>
Installation of PyHIST can be performed in three different ways:
* [Through a Docker image](#docker) (Linux/macOS/Windows)
* [Conda environment](#conda) (Linux/macOS)
* [Standalone](#standalone) (Linux)
 To install locally, skip to the [installation](#installation) section.

### PyHIST Docker image (Windows/macOS/Linux)<a name="docker"></a>
The Docker image described in this section contains all the necessary dependencies to run PyHIST. The public Docker image for PyHIST can be downloaded from the Docker Hub:
```shell
docker pull mmunozag/pyhist
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

### Conda environment (macOS/Linux)<a name="conda"></a>
Clone the respository and move into the folder:
```shell
git clone https://github.com/manuel-munoz-aguirre/PyHIST.git
cd PyHIST
```

A `conda` environment with all the necessary Python dependencies can be created with:
```
conda env create -f conda/environment.yml
```

Compile the segmentation tool:
```
cd src/graph_segmentation/
make
```

### Standalone installation (Linux)<a name="standalone"></a>
Clone the repository and simply use PyHIST as python script (see [quickstart](#usescript)). PyHIST has the following dependencies:
* Python (>3.6):
  * openslide-python, opencv-python, pandas, numpy, Pillow
* Other:
  * openslide-tools, pixman==0.36.0


## Quickstart<a name="quickstart"></a>
### Using the Docker image<a name="usedocker"></a>
PyHIST can be directly executed using Docker. Replace `<dockerimg>` by `mmunozag/pyhist` if you pulled the image from Dockerhub, or simply `pyhist` if you built the image yourself.

```shell
docker run <dockerimg> --help
```

To mount a local folder `/path_with/images/` mapping to the folder `/pyhist/images/` inside the container, use the `-v` flag specifying the absolute path of the local folder. 
```shell
docker run -v /path_with/images/:/pyhist/images/ <dockerimg> [args]
```

Optionally, if you want to ensure that all the generated output files are written with permissions belonging to the current host user (instead of `root`, which is Docker's default), specify the username and group with the `-u` flag (retrieval of both can be automated with `id` ), as well mapping the `passwd` file with a second `-v` flag: 
```shell
docker run -v /path_with/images/:/pyhist/images/ \
	-u $(id -u):$(id -g) \ 
	-v /etc/passwd:/etc/passwd \
	<dockerimg> [args]
```

A working example to process an image called `test.svs` located inside `/path_with/images/`:
```shell
docker run -v /path_with/images/:/pyhist/images/ \
	-u $(id -u):$(id -g) \
	-v /etc/passwd:/etc/passwd \
	<dockerimg> --save-tilecrossed-image --output images/ images/test.svs
```

### Using PyHIST<a name="usescript"></a>
PyHIST can be directly executed as a script. To see all available options:
```
python pyhist.py --help
```

A working example to process an image called `test.svs` located inside `/path_with/images/`:
```
python pyhist.py \
	--content-threshold 0.05 \
	--patch-size 64 \
	--output-downsample 16 \
	--info "verbose" \
	--save-tilecrossed-image\
	/path_with/images/test.svs
```

## Documentation <a name="documentation"></a>
PyHIST's [documentation](https://pyhist.readthedocs.io/) explains in detail the installation steps and all available arguments and processing modes, as well as [tutorial](https://pyhist.readthedocs.io/en/latest/tutorial/) with examples to perform histological image segmentation, random tile sampling, and explanations of the steps of the segmentation pipeline. An example [use case](https://pyhist.readthedocs.io/en/latest/testcase/) with a sample of The Cancer Genome Atlas WSIs is also available to demonstrate how to use PyHIST to prepare data for a machine learning application.
