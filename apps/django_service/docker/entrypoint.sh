#!/bin/sh
set -eu

echo "===> Applying DM migrations..."
python manage.py migrate

echo "===> Starting Django service..."
exec python manage.py runserver 0.0.0.0:8000
