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
sudo ln -s /var/www/api.openbikes.co/deployment/ /etc/nginx/sites-available/api.openbikes.co
```

`/etc/nginx/sites-available/api.openbikes.co`:
```
server {
    listen 80;
    listen [::]:80;
    server_name api.openbikes.co www.api.openbikes.co;
    return 301 https://$server_name$request_uri;
}

server {

    # SSL configuration

    listen 443 ssl;
    listen [::]:443 ssl;

    ssl_certificate /etc/letsencrypt/live/api.openbikes.co/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.openbikes.co/privkey.pem;

        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_prefer_server_ciphers on;
        ssl_dhparam /etc/ssl/certs/dhparam.pem;
        ssl_ciphers 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:AES:CAMELLIA:DES-CBC3-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA';
        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;
        ssl_stapling on;
        ssl_stapling_verify on;
        add_header Strict-Transport-Security max-age=15768000;


    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/api.openbikes.co/openbikes.sock;
    }

    location ~ /.well-known {
        allow all;
    }
}
```

```sh
sudo ln -s /etc/nginx/sites-available/api.openbikes.co /etc/nginx/sites-enabled
```

You can test for syntax errors by typing :
```sh
sudo nginx -t
```
If this returns without indicating any issues, we can restart the Nginx process to read the our new config:

```sh
sudo service nginx restart
sudo start api.openbikes.co
```

Deployment done.
