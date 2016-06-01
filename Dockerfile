FROM ubuntu:14.04

RUN apt-get update && apt-get install -y \
    gfortran \
    libatlas-base-dev \
    libblas-dev \
    libpq-dev \
    libxml2-dev \
    libxslt-dev \
    postgis \
    postgis* \
    python3-dev \
    python3-pip \
    python3-lxml

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app
