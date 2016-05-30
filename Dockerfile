FROM ubuntu:14.04

RUN apt-get update && apt-get install -y \
    python3-pip \
    libpq-dev \
    postgis

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app