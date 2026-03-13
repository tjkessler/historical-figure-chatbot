#!/bin/bash
# Script to start the FastAPI backend using uvicorn

# Default host and port
HOST="0.0.0.0"
PORT="8000"

# Allow overriding host and port via arguments
if [ ! -z "$1" ]; then
  HOST="$1"
fi
if [ ! -z "$2" ]; then
  PORT="$2"
fi

# Start the backend
uvicorn backend.main:app --host "$HOST" --port "$PORT" --reload
