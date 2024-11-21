#!/bin/sh

set -e

host="$1"
shift

until curl -sf -k -L http://$host:8000/api/core/health/ > /dev/null; do
  echo "Backend is unavailable - sleeping"
  sleep 5
done

echo "Backend is up - executing command"
exec "$@"
