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
	ln -s app/config_dev.py app/config.py

# Set up production environment
prod:
	ln -s app/config_prod.py app/config.py