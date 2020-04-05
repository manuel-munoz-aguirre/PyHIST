FROM debian:stable

LABEL maintainer "Manuel Muñoz <manuel.munoz@crg.eu>" \
      version "1.0" \
      description "Docker image for PyHIST"

# Install necessary tools
RUN export DEBIAN_FRONTEND=noninteractive && \
	apt-get update --fix-missing -qq && \
	apt-get install -y -q \
	build-essential \
	libgl1-mesa-glx \
	python3.6 \
	python3-pip \
	openslide-tools \
	python3-openslide && \
	pip3 install pandas opencv-python

# Copy PyHIST to container
WORKDIR /pyhist
COPY pyhist* /pyhist/
ADD src /pyhist/src

# Compile segmentation algorithm
RUN cd src/graph_segmentation/ && \
	make && \
	chmod 755 segment

# Entrypoing
ENTRYPOINT ["python3", "pyhist.py"]
