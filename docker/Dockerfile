FROM debian:stable

LABEL maintainer "Manuel Muñoz <manuel.munoz@crg.eu>" \
      version "1.0" \
      description "Docker image for PyHIST"

# install needed tools
RUN export DEBIAN_FRONTEND=noninteractive && \
	apt-get update --fix-missing -qq && \
	apt-get install -y -q \
	build-essential \
	libgl1-mesa-glx \
	python3.6 \
	python3-pip \
	openslide-tools \
	python3-openslide

RUN pip3 install pandas opencv-python

# Copy script
WORKDIR /pyhist
COPY pyhist* /pyhist/
ADD src /pyhist/src
