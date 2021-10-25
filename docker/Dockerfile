FROM mambaorg/micromamba:0.14.0 AS builder

LABEL maintainer "Manuel Muñoz <manuel.munoz@crg.eu>" \
      version "1.0" \
      description "Docker image for PyHIST"

# Copy yml file for the conda environment
COPY conda/environment.yml /tmp/env.yaml

# Install necessary tools and pack python environment for pyhist
RUN apt-get update -qq && \
	apt-get install -y -q build-essential && \
	micromamba install -y -c conda-forge conda-pack && \
	micromamba env create -f /tmp/env.yaml && \
	conda-pack -p /opt/conda/envs/pyhist -o /tmp/env.tar &&\
	micromamba remove -p /op/conda/envs/pyhist --all -y &&
	micromamba clean --all --yes

# Unpack pyhist environment
WORKDIR /pyhist
RUN mkdir env && cd env && \
	tar xf /tmp/env.tar && \
	rm /tmp/env.tar && \
	/pyhist/env/bin/conda-unpack

# Copy PyHIST to container
COPY pyhist* .
COPY src src

# Compile segmentation algorithm
RUN cd src/graph_segmentation/ && \
	make && \
	chmod 755 segment

# Build final, Slim image.
FROM debian:buster-slim
RUN apt-get update -qq && \
	rm -rf /var/lib/apt/lists/*
WORKDIR /pyhist
COPY --from=builder /pyhist /pyhist
ENV PATH="/pyhist/env/bin:$PATH"
ENTRYPOINT ["python", "pyhist.py"]
