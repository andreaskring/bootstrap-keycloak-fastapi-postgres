#!/bin/bash
set -o nounset
set -o errexit
set -o pipefail

# Run app
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Running in development mode (hot-reload)"
    uvicorn backend.main:app --host 0.0.0.0 --reload
else
    echo "Running in production mode"
    uvicorn backend.main:app --host 0.0.0.0
fi
