Installation of PyHIST can be performed in three different ways:

* [Through a Docker image](#docker) (Linux/macOS/Windows)
* [Conda environment](#conda) (Linux/macOS)
* [Standalone](#standalone) (Linux/macOS)
 

### PyHIST Docker image (Linux/macOS/Windows)<a name="docker"></a>
The Docker image described in this section contains all the necessary dependencies to run PyHIST. The public Docker image for PyHIST can be downloaded from the Docker Hub:
```shell
docker pull mmunozag/pyhist
```

After downloading it, you can skip directly to [Quickstart: Using the Docker image](quickstart.md). Alternatively, you can build the Docker image on your own by using the Dockerfile in this repository. Clone the respository and move into the folder:
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

Then, PyHIST can be simply used as a python script (see [quickstart](quickstart.md)).

### Standalone installation (Linux/macOS)<a name="standalone"></a>
Although we recommend isolating all the dependencies in a conda environment as above, PyHIST can be simply used as a python script (see [quickstart](quickstart.md)) as long as the following dependencies are met:

* Python (>3.6):
  * openslide-python, opencv-python, pandas, numpy, Pillow
* Other:
  * openslide-tools, pixman==0.36.0