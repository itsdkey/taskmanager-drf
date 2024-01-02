#!/bin/sh

set -e

python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:${DJANGO_PORT}
