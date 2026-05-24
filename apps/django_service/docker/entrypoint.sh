#!/bin/sh
set -eu

echo "===> Starting Django service..."
exec python manage.py runserver 0.0.0.0:8000
