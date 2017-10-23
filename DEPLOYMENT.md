# Deployment

```sh
# Virtual environment
conda create -n openbikes python=3.6
source activate openbikes

# PostgreSQL
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres psql
psql
CREATE DATABASE openbikes
\q

# Clone
git clone https://github.com/OpenBikes/api.openbikes.co
pip install -r requirements.txt
```
