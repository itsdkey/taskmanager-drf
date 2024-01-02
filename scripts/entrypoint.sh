#!/bin/sh

set -e

# we dont need to collectstatic each time
# python manage.py collectstatic --noinput
python manage.py wait_for_db
uwsgi --socket :${DJANGO_PORT} \
  --workers 4 \
  --master \
  --enable-threads \
  --module taskmanager.wsgi
