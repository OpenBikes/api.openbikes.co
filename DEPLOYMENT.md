# Deployment

```sh
# PostgreSQL
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres psql postgres
\password postgres
CREATE DATABASE openbikes;
\q

# Clone
git clone https://github.com/OpenBikes/api.openbikes.co
cd api.openbikes.co
chmod 777 -R *

# Virtual environment
conda create -n openbikes python=3.6
source activate openbikes
pip install -r requirements.txt

# Environment variables
nano .env

# Migrations
python manage.py migrate

# Add cities
chmod +x scripts/add-cities.sh
./scripts/add-cities.sh

# Crontab
crontab schedule
```
