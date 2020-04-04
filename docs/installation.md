The Docker image described in the section below contains all the necessary dependencies to run PyHIST. Otherwise, to install locally, skip to the [installation](#installation) section.

# PyHIST Docker image
The public Docker image for PyHIST can be downloaded from the Docker Hub:
```shell
docker pull mmunozag/pyhist
```

After downloading it, you can skip directly to [Quickstart: Using the Docker image](#usedocker). Alternatively, you can build the Docker image on your own by using the Dockerfile in this repository. Clone the respository and move into the folder:
```shell
git clone https://github.com/manuel-munoz-aguirre/PyHIST.git
cd PyHIST
```

Build the Docker image with the following command:
```shell
docker build -f docker/Dockerfile -t pyhist .
```

# Installation<a name="installation"></a>
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

PyHIST has the following dependencies:
* Python (>3.6):
  * openslide, pandas, numpy, PIL, cv2
* Other:
  * openslide-tools, libgl1-mesa-glx, pixman==0.36.0
