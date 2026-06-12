#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -f .env ]]; then
  echo "Missing .env — copy .env.example to .env and fill in values." >&2
  exit 1
fi

PYTHON="${PYTHON:-python3.11}"
if ! command -v "$PYTHON" &>/dev/null; then
  PYTHON=python3
fi

VENV_DIR=".venv"
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtualenv with $PYTHON..."
  "$PYTHON" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "Installing dependencies..."
pip install -q -r requirements.txt

set -a
# shellcheck disable=SC1091
source .env
set +a

export DB_HOST=localhost
export DB_PORT=3306

COMPOSE=(docker compose -f docker-compose.db.yml -f docker-compose.db.dev.yml)

echo "Starting database..."
"${COMPOSE[@]}" up -d --wait

echo "Running migrations..."
until alembic upgrade head; do
  echo "Waiting for database..."
  sleep 2
done

echo "Starting app at http://127.0.0.1:8090"
exec gunicorn \
  --bind 127.0.0.1:8090 \
  --workers 1 \
  --threads 4 \
  --timeout 120 \
  app:app
