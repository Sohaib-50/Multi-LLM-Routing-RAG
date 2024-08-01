#!/bin/bash

# Navigate to the backend directory
cd /app/backend

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Start the server
exec "$@"
