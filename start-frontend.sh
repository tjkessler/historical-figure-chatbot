#!/bin/bash
# Script to start the frontend in development mode using Vite

# Default host and port
HOST="localhost"
PORT="3000"

# Allow overriding host and port via arguments
if [ ! -z "$1" ]; then
  HOST="$1"
fi
if [ ! -z "$2" ]; then
  PORT="$2"
fi

# Start the frontend (assumes Vite is installed and package.json scripts are set up)
cd frontend || { echo "Frontend directory not found"; exit 1; }

# Use npm if available, otherwise try yarn
if command -v npm &> /dev/null; then
  npm run dev -- --host "$HOST" --port "$PORT"
elif command -v yarn &> /dev/null; then
  yarn dev --host "$HOST" --port "$PORT"
else
  echo "Neither npm nor yarn is installed. Please install one to continue."
  exit 1
fi
