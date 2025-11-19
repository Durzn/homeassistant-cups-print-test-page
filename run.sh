#!/usr/bin/env bash
echo "Starting CUPS Print Addon..."
gunicorn -b 0.0.0.0:5000 cups_server:app