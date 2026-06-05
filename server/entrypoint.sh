#!/bin/sh
set -e

until alembic upgrade head; do
  echo "Waiting for database..."
  sleep 2
done

exec flask run
