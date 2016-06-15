FROM ubuntu:14.04

RUN apt-get update && apt-get install -y \
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
    python3.4-dev \
    rsyslog

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

# Add the crontab file and the script to start it
ADD scripts/etc/crontab /etc/crontab
ADD scripts/bin/start-cron.sh /usr/bin/start-cron.sh
RUN chmod +x *.py /usr/bin/start-cron.sh
RUN touch /var/log/cron.log
