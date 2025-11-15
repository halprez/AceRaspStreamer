#!/bin/bash

set -e

HTTP_PORT=${HTTP_PORT:-6878}
EXTRA_FLAGS=""

if [[ "$ALLOW_REMOTE_ACCESS" == "yes" ]]; then
    EXTRA_FLAGS="$EXTRA_FLAGS --bind-all"
fi

echo "==================================="
echo "Acestream HTTP Proxy ARM64"
echo "Port: $HTTP_PORT"
echo "Remote Access: $ALLOW_REMOTE_ACCESS"
echo "==================================="

cd /opt/acestream

# Find the engine binary
ENGINE=""
if [ -f "./acestreamengine" ]; then
    ENGINE="./acestreamengine"
elif [ -f "./acestreamengine.AndroidPlayer" ]; then
    ENGINE="./acestreamengine.AndroidPlayer"
else
    echo "ERROR: Acestream engine binary not found!"
    echo "Available files:"
    ls -la /opt/acestream/
    exit 1
fi

echo "Starting engine: $ENGINE"

# Start the engine
exec $ENGINE \
    --client-console \
    --http-port $HTTP_PORT \
    $EXTRA_FLAGS
