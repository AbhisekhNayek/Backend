#!/bin/bash
set -e

# Run tests before starting the server? (Optional, usually done in CI/CD pipeline, not runtime)

# Start Gunicorn with Uvicorn workers
exec gunicorn app.main:app -c gunicorn_conf.py
