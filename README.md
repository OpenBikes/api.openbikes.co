# OpenBikes API

## Running Docker locally

Install the [Docker toolbox](https://www.docker.com/products/docker-toolbox) and then run the following commands.

```sh
docker-machine create -d virtualbox dev;
eval "$(docker-machine env dev)"
docker-compose build
docker-compose up -d
```


# Makefile commands

## Dev environment

#### `make install`

Install `requirements.txt`.

#### `make test`

Compute tests with **nosetests**.

## Configuration

**Flask** needs a `config.py` file located in `app/` in order to launch the web service.

#### `make dev`

`make dev` creates a symbolink link with `config_dev.py` and `config.py`.

#### `make prod`
`make dev` creates a symbolink link with `config_prod.py` and `config.py`.

## Setup

#### `make init`
Init database.

#### `make drop`
Drop database.

#### `make bikes`
Launch bikes collecting.

#### `make weather`
Launch weather collecting.

#### `make train`
Train regressors.
