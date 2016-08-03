FROM phusion/baseimage:0.9.19
MAINTAINER OpenBikes

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]

ENV TERM=xterm-256color

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
    python3-pip

# Install Python requirements
RUN mkdir -p /usr/src/app
COPY ../requirements.txt /usr/src/app/
RUN pip3 install --upgrade pip
RUN pip3 install -r /usr/src/app/requirements.txt

# Copy the files from the host to the container
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN chmod 777 -R *

# Add the crontab file
ADD scripts/etc/crontab /etc/cron.d/jobs
RUN chmod 777 /etc/cron.d/jobs
RUN chmod 777 /etc/crontab
RUN touch /var/log/cron.log
RUN /usr/bin/crontab /etc/cron.d/jobs

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
