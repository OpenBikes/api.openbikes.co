# OpenBikes Makefile

## Configuration

BUILD_TIME := $(shell date +%FT%T%z)
PROJECT    := $(shell basename $(PWD))

## Commands

all: install 

# Install dependencies
install:
	pip3 install -r requirements.txt

# Compute some tests
test:
	nosetests

# Set up developpement environment
dev:
	[ -f app/config_dev.py ] && ln -sfn app/config_dev.py app/config.py || echo "File config_dev.py does not exist"

# Set up production environment
prod:
	[ -f app/config_prod.py ] && ln -sfn app/config_prod.py app/config.py || echo "File config_prod.py does not exist"

