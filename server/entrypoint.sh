#!/bin/sh
set -e

until alembic upgrade head; do
  echo "Waiting for database..."
  sleep 2
done

# Single worker: in-process job dedup in analysis_runner requires one process.
exec gunicorn \
  --bind 0.0.0.0:8090 \
  --workers 1 \
  --threads 4 \
  --timeout 120 \
  app:app
