> How To Serve Flask Applications with Gunicorn and Nginx on Ubuntu 14.04

## Prerequisites

- Ubuntu 14.04  
- Flask App  
- Gunicorn

## Install the Components from the Ubuntu Repositories

```sh
sudo apt-get update
sudo apt-get install python-pip python-dev nginx
```

## Create a Python Virtual Environment

```sh
sudo pip install virtualenv
```

## Create the WSGI Entry Point

```sh
sudo vim /var/www/api.openbikes.co/wsgi.py
```

And add this :

`/var/www/api.openbikes.co/wsgi.py`:
```python
import sys, os, logging
logging.basicConfig(stream=sys.stderr)

sys.path.insert(0, '/var/www/api.openbikes.co')
os.chdir('/var/www/api.openbikes.co')

from app import app

application = app

if __name__ == "__main__":
    application.run()
```

## Create an Upstart Script

```sh
sudo vim /etc/init/openbikes.conf
```
Creating an Upstart script will allow Ubuntu's init system to automatically start Gunicorn and serve our Flask application whenever the server boots.

`/etc/init/openbikes.conf`: 
```
description "Gunicorn application server running openbikes"

start on runlevel [2345]
stop on runlevel [!2345]

respawn
setuid max
setgid www-data

env PATH=/var/www/api.openbikes.co/openbikes/bin
chdir /var/www/api.openbikes.co
exec gunicorn --workers 3 --bind unix:openbikes.sock -m 007 wsgi
```

## Configuring Nginx to Proxy Requests

Our Gunicorn application server should now be up and running, waiting for requests on the socket file in the project directory. We need to configure Nginx to pass web requests to that socket by making some small additions to its configuration file.

```sh
sudo vim /etc/nginx/sites-available/openbikes
``` 

`/etc/nginx/sites-available/openbikes`: 
```
server {
    listen 80;
    server_name www.openbikes.co;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/api.openbikes.co/openbikes.sock;
    }

}
```

```sh
sudo ln -s /etc/nginx/sites-available/openbikes /etc/nginx/sites-enabled
```

You can test for syntax errors by typing :
```sh
sudo nginx -t
```
If this returns without indicating any issues, we can restart the Nginx process to read the our new config:

```sh
sudo service nginx restart
sudo start openbikes
``` 

Deployment done.