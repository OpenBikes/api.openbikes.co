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

#### `make dev`

**Flask** needs a `config.py` file located in `app/` in order to launch the web service.
`make dev` creates a symbolink link with `config_dev.py` and `config.py`.

#### `make prod`
`make dev` creates a symbolink link with `config_prod.py` and `config.py`.

