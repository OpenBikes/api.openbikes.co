# api.openbikes.co Makefile

## Configuration

BUILD_TIME := $(shell date +%FT%T%z)
PROJECT    := $(shell basename $(PWD))

## Commands

.PHONY: docker.create
docker.create:
	docker-machine create -d virtualbox --virtualbox-memory 512 --virtualbox-cpu-count 1 dev
	docker-machine env dev
	eval "$(docker-machine env dev)"

.PHONY: docker.build
docker.build:
	docker-compose build

.PHONY: docker.launch
docker.launch:
	docker-compose up -d


### Install dependencies
.PHONY: install
install:
	pip3 install -r requirements.txt

### Run tests
.PHONY: test
test:
	nosetests

### Setup developpement environment
.PHONY: dev
dev:
	cd app && ln -sf config_dev.py config.py

### Setup production environment
.PHONY: prod
prod:
	cd app && ln -sf config_prod.py config.py
