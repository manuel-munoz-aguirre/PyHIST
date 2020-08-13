Installation of PyHIST can be performed in three different ways:
* [Through a Docker image](#docker) (Linux/macOS/Windows)
* [Conda environment](#conda) (Linux/macOS)
* [Standalone](#standalone) (Linux/macOS)
 To install locally, skip to the [installation](#installation) section.

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