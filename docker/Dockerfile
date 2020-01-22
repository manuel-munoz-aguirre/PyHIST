# Build conda environment
FROM continuumio/miniconda3
LABEL maintainer "Manuel Munoz <manuel.munoz@crg.eu>" \
	version "1.0" \
	description "Docker image for PyHIST"

# Create environment and activate it upon initialization
ADD docker/environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml
RUN echo "source activate $(head -1 /tmp/environment.yml | cut -d' ' -f2)" > ~/.bashrc
ENV PATH /opt/conda/envs/$(head -1 /tmp/environment.yml | cut -d' ' -f2)/bin:$PATH

# Install build utilities
RUN apt-get update --fix-missing -qq && \
	apt-get install -y -q build-essential \
	libmagickwand-dev \
	libgl1-mesa-glx && \
	conda install pixman=0.36.0

# Copy script
WORKDIR /pyhist
COPY pyhist* /pyhist/
ADD src /pyhist/src

# Compile segmentation binary
RUN cd src/graph_segmentation/ && \
	make
