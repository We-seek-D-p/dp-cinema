#!/bin/sh
set -eu

echo "===> Starting Fastapi service..."
exec uvicorn main:app --host 0.0.0.0 --port 8001 --reload