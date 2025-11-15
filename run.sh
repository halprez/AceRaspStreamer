#!/bin/bash

set -e

# Set defaults
HTTP_PORT=${HTTP_PORT:-6878}
EXTRA_FLAGS=""

if [[ $ALLOW_REMOTE_ACCESS == "yes" ]]; then
    EXTRA_FLAGS="$EXTRA_FLAGS --bind-all"
fi

# Check if we're running the Android-based engine
if [ -f "/opt/acestream/acestreamengine.AndroidPlayer" ]; then
    # Android-based engine (from APK)
    echo "Starting Acestream Engine (Android-based) on port $HTTP_PORT..."
    cd /opt/acestream
    
    # Set up environment for Android binaries
    export LD_LIBRARY_PATH=/opt/acestream:$LD_LIBRARY_PATH
    
    # Start the engine
    exec ./acestreamengine.AndroidPlayer \
        --client-console \
        --http-port $HTTP_PORT \
        $EXTRA_FLAGS
else
    # Fallback: try standard Linux engine
    echo "Starting Acestream Engine (Linux) on port $HTTP_PORT..."
    exec /opt/acestream/start-engine \
        --client-console \
        --http-port $HTTP_PORT \
        $EXTRA_FLAGS
fi
