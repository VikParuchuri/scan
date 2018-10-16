#!/usr/bin/env bash

apt-get update -y
apt-get install build-essential -y
cd /vagrant
xargs -a apt-packages.txt apt-get install -y
pip install -r pre-requirements.txt -i https://pypi.python.org/simple
pip install -r requirements.txt -i https://pypi.python.org/simple
PYTHONPATH=. alembic upgrade head

service scan start
service celery start