#!/usr/bin/env bash
set -e

# Fix ownership of the data volume (runs as root)
chown -R appuser:appgroup /app/data

# Drop to appuser and exec the CMD
exec gosu appuser "$@"
