# OpenBikes API

## Running Docker locally

Install the [Docker toolbox](https://www.docker.com/products/docker-toolbox) and then run the following commands.

```sh
docker-machine create -d virtualbox dev;
eval "$(docker-machine env dev)"
docker-compose build
docker-compose up -d
```


## Using Makefile

#### `make install`

Install `requirements.txt`.

#### `make test`

Compute tests with **nosetests**.