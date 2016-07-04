 FROM ubuntu:14.04

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Install necessary packages
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    gfortran \
    libatlas-base-dev \
    libblas-dev \
    libpq-dev \
    libxml2-dev \
    libxslt-dev \
    postgis \
    postgis* \
    python3.4 \
    python3.4-dev

# Install pip3
ADD https://raw.githubusercontent.com/pypa/pip/5d927de5cdc7c05b1afbdd78ae0d1b127c04d9d0/contrib/get-pip.py /root/get-pip.py
RUN python3.4 /root/get-pip.py
RUN pip3 install --upgrade pip

# Install Python requirements
RUN mkdir -p /usr/src/app
COPY requirements.txt /usr/src/app/
RUN pip3 install -r /usr/src/app/requirements.txt

# Copy the files from the host to the container
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN chmod 777 -R *

# Add the crontab file
ADD scripts/etc/crontab /etc/crontab
