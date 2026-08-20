#!/bin/sh

set -eu


database_path="${DJANGO_DATABASE_PATH:-/data/db.sqlite3}"
database_directory="$(dirname "$database_path")"


echo "Preparing database directory: $database_directory"
mkdir -p "$database_directory"


echo "Applying Django database migrations..."
python manage.py migrate --noinput


echo "Collecting Django static files..."
python manage.py collectstatic --noinput


echo "Starting Literature Lab..."
exec "$@"
