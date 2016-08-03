# Running Docker

Install the [Docker toolbox](https://www.docker.com/products/docker-toolbox) and then run the following commands for either running Docker locally or in production.

## In development

[Tutorial](https://realpython.com/blog/python/dockerizing-flask-with-compose-and-machine-from-localhost-to-the-cloud/)

```sh
cd ~/path/to/api.openbikes.co/
docker-machine env dev
eval "$(docker-machine env dev)"
docker-compose build
docker-compose up -d
docker-compose run web make dev
docker-compose run web python3 manage.py initdb
docker-compose run web ./scripts/add-cities.sh
```

- Don't forget to `docker-machine stop dev` when you're done so that the container stops running in the background.
- Run `docker-machine start dev` to boot up the dev container the next time you want to use it.
- If you encounter a problem then you can `docker-machine rm dev` and start again.
- A good internet connection makes the process painless.
- You can access the application on the host by accessing `docker-machine ip dev`
- Access logs with `docker-compose logs`
- Start the cron jobs with `service cron start` after having logged into the container with `docker-compose run web /bin/sh`

## In production

[Tutorial](https://docs.docker.com/machine/examples/ocean/)

```sh
cd ~/path/to/api.openbikes.co/
docker-machine create --driver digitalocean --digitalocean-access-token <DIGITAL_OCEAN_TOKEN> --digitalocean-size "2gb" --digitalocean-region "FRA1" prod
docker-machine env prod
eval "$(docker-machine env prod)"
docker-compose build
docker-compose up -d
docker-compose run web make prod
docker-compose run web python3 manage.py initdb
docker-compose run web ./scripts/add-cities.sh
```
