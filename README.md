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

<a href='https://travis-ci.com/github/manuel-munoz-aguirre/PyHIST'>
<img src='https://travis-ci.com/manuel-munoz-aguirre/PyHIST.svg?branch=master' alt='Travis CI' />
</a>
</h1>

[About PyHIST](#about) | [Setup](#setup) | [Quickstart](#quickstart) | [Documentation](#documentation) | [References](#references) | [Citation](#citation)

## About PyHIST<a name="about"></a>

PyHIST is a **H**istological **I**mage **S**egmentation **T**ool: a lightweight semi-automatic pipeline to extract tiles with foreground content from SVS histopathology whole image slides (with experimental support for [other formats](#documentation)). It is intended to be an easy-to-use tool to preprocess histological image data for usage in machine learning tasks. The PyHIST pipeline involves three main steps: 1) produce a mask for the input WSI that differentiates the tissue from the background, 2) create a grid of tiles on top of the mask, evaluate each tile to see if it meets the minimum content threshold to be considered as foreground and 3) extract the selected tiles from the input WSI at the requested resolution.

<div align="center">
<img src="https://raw.githubusercontent.com/manuel-munoz-aguirre/PyHIST/master/docs/resources/how_pyhist_works.png" alt="logo" width=600></img>
</div>

## Setup<a name="setup"></a>
Installation of PyHIST can be performed in three different ways:
* [Through a Docker image](#docker) (Linux/macOS/Windows)
* [Conda environment](#conda) (Linux/macOS)
* [Standalone](#standalone) (Linux/macOS)

### PyHIST Docker image (Linux/macOS/Windows)<a name="docker"></a>
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
docker build -f docker/Dockerfile -t mmunozag/pyhist .
```

### Conda environment (Linux/macOS)<a name="conda"></a>
Clone the respository and move into the folder:
```shell
git clone https://github.com/manuel-munoz-aguirre/PyHIST.git
cd PyHIST
```

A `conda` environment with all the necessary Python dependencies can be created with:
```
conda env create -f conda/environment.yml
```

Then, PyHIST can be simply used as a python script (see [quickstart](#usescript)).

### Standalone installation (Linux/macOS)<a name="standalone"></a>
Although we recommend isolating all the dependencies in a conda environment as above, PyHIST can be simply used as a python script (see [quickstart](#usescript)) as long as the following dependencies are met:
* Python (>3.6):
  * openslide-python, opencv-python, pandas, numpy, Pillow
* Other:
  * openslide-tools, pixman==0.36.0


## Quickstart<a name="quickstart"></a>
### Using the Docker image<a name="usedocker"></a>
PyHIST can be directly executed using Docker.
```shell
docker run mmunozag/pyhist --help
```

To mount a local folder `/path_with/images/` mapping to the folder `/pyhist/images/` inside the container, use the `-v` flag specifying the absolute path of the local folder. 
```shell
docker run -v /path_with/images/:/pyhist/images/ mmunozag/pyhist [args]
```

Optionally, if you want to ensure that all the generated output files are written with permissions belonging to the current host user (instead of `root`, which is Docker's default), specify the username and group with the `-u` flag (retrieval of both can be automated with `id` ), as well mapping the `passwd` file with a second `-v` flag: 
```shell
docker run -v /path_with/images/:/pyhist/images/ \
	-u $(id -u):$(id -g) \ 
	-v /etc/passwd:/etc/passwd \
	mmunozag/pyhist [args]
```

A working example to process an image called `test.svs` located inside `/path_with/images/`:
```shell
docker run -v /path_with/images/:/pyhist/images/ \
	-u $(id -u):$(id -g) \
	-v /etc/passwd:/etc/passwd \
	mmunozag/pyhist --save-tilecrossed-image --output images/ images/test.svs
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

## Citation <a name="citation"></a>
PyHIST is published in a PLOS Computational Biology software article ([doi: 10.1371/journal.pcbi.1008349](https://doi.org/10.1371/journal.pcbi.1008349)). If you find PyHIST useful, consider citing as:

```
Muñoz-Aguirre, M., Ntasis, V. F., Rojas, S. & Guigó, R. PyHIST: A Histological Image Segmentation Tool. PLoS Computational Biology 16, e1008349 (2020).

@article{MunozAguirre2020,
  doi = {10.1371/journal.pcbi.1008349},
  url = {https://doi.org/10.1371/journal.pcbi.1008349},
  year = {2020},
  month = oct,
  publisher = {Public Library of Science ({PLoS})},
  volume = {16},
  number = {10},
  pages = {e1008349},
  author = {Manuel Mu{\~{n}}oz-Aguirre and Vasilis F. Ntasis and Santiago Rojas and Roderic Guig{\'{o}}},
  title = {{PyHIST}: A Histological Image Segmentation Tool},
  journal = {{PLOS} Computational Biology}
}
```
