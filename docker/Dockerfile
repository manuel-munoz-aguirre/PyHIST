# Build conda environment
FROM continuumio/miniconda3

# Create environment
ADD docker/environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml

LABEL maintainer "Manuel Munoz <manuel.munoz@crg.eu>" \
	version "1.0" \
	description "Docker image for HistologySegment"

# Activate environment on initialization
RUN echo "source activate $(head -1 /tmp/environment.yml | cut -d' ' -f2)" > ~/.bashrc
ENV PATH /opt/conda/envs/$(head -1 /tmp/environment.yml | cut -d' ' -f2)/bin:$PATH

# Install build utilities
RUN apt-get update --fix-missing -qq && \
	apt-get install -y -q build-essential \
	libmagickwand-dev

# Copy script
WORKDIR /segment_hist
COPY segment_hist* /segment_hist/
ADD src /segment_hist/src

# Compile segmentation binary
RUN cd src/Felzenszwalb_algorithm/ && \
	make
