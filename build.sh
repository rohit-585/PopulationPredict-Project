#!/usr/bin/env bash
set -o errexit

# Install system dependencies for psycopg2
apt-get update
apt-get install -y libpq-dev gcc

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
