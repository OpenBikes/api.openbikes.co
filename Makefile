# api.openbikes.co Makefile

## Configuration

BUILD_TIME := $(shell date +%FT%T%z)
PROJECT    := $(shell basename $(PWD))

## Commands

all:
	install

### Install dependencies
install:
	pip3 install -r requirements.txt

### Run tests
test:
	nosetests

### Setup developpement environment
dev:
	[ -f app/config_dev.py ] && ln -sfn app/config_dev.py app/config.py || echo "File config_dev.py does not exist"

### Setup production environment
prod:
	ln -s app/config_prod.py app/config.py
	[ -f app/config_prod.py ] && ln -sfn app/config_prod.py app/config.py || echo "File config_prod.py does not exist"
