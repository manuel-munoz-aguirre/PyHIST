ARG DEBIAN_FRONTEND=noninteractive
FROM python:3.6 as builder

LABEL maintainer "Manuel Muñoz <manuel.munoz@crg.eu>" \
      version "1.0" \
      description "Docker image for PyHIST"

# Install necessary tools
RUN apt-get update -qq && \
	apt-get install -y -q \
	libgl1-mesa-glx \
	openslide-tools

# Copy PyHIST to container
WORKDIR /opt/pyhist
RUN python -m venv venv \
	&& ./venv/bin/python -m pip install --no-cache-dir -U pip setuptools wheel \
	&& ./venv/bin/python -m pip install --no-cache-dir pandas opencv-python openslide-python
ENV PATH="/opt/pyhist/venv/bin:$PATH"
COPY pyhist* .
COPY src src

# Compile segmentation algorithm
RUN cd src/graph_segmentation/ && \
	make && \
	chmod 755 segment

# Build final, slim image.
FROM python:3.6-slim
RUN apt-get update -qq \
	&& apt-get install -y -q \
		libgl1-mesa-glx \
		libopenslide0 \
	&& rm -rf /var/lib/apt/lists/*
WORKDIR /opt/pyhist
COPY --from=builder /opt/pyhist .
ENV PATH="/opt/pyhist/venv/bin:$PATH"
ENTRYPOINT ["python3", "pyhist.py"]
