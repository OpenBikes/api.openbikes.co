# api.openbikes.co Makefile

## Configuration

BUILD_TIME := $(shell date +%FT%T%z)
PROJECT    := $(shell basename $(PWD))

## Commands

### Install dependencies
install:
	pip3 install -r requirements.txt

### Run tests
test:
	nosetests

### Setup developpement environment
dev:
	ln -s app/config_dev.py app/config.py

### Setup production environment
prod:
	ln -s app/config_prod.py app/config.py
