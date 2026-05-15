#!/bin/sh
set -eu

echo "===> Launching Celery worker for transcoding video..."
exec celery -A core.celery_app:celery_app worker -l info