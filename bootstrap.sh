#!/usr/bin/env bash

apt-get update -y
apt-get install build-essential -y
cd /vagrant
xargs -a apt-packages.txt apt-get install -y

pip install -r pre-requirements.txt
pip install -r requirements.txt
alembic upgrade head

service scan start
service celery start