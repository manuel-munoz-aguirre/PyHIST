The Docker image described in the section below contains all the necessary dependencies to run PyHIST. Otherwise, to install locally, skip to the [installation](#installation) section.

# PyHIST Docker image

The public docker image for PyHIST can be downloaded from the Docker Hub:
```
docker pull [TO DO]
```

After downloading it, you can skip directly to Quickstart: Using the Docker image. Alternatively, you can build the Docker image on your own by using the Dockerfile in this repository. Clone the respository and move into the folder:
```
git clone https://github.com/manuel-munoz-aguirre/PyHIST.git
cd PyHIST
```

Build the docker image with the following command:
```
docker build -f docker/Dockerfile -t pyhist .
```

# Installation<a name="installation"></a>

Clone the respository and move into the 
```
git clone https://github.com/manuel-munoz-aguirre/PyHIST.git
cd PyHIST
```

PyHIST has the following dependencies:

	Python (>3.6):
		Openslide, pandas, numpy, PIL, cv2
	Other:
		libgl1-mesa-glx

A conda environment with all the necessary Python dependencies can be created with:
```
conda env create -f docker/environment.yml
```

Compile the segmentation tool:
```
cd src/graph_segmentation/
make
```
