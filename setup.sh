#!/bin/bash

set -e

echo "================================================"
echo "Acestream ARM64 Setup for Raspberry Pi 5"
echo "================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Install it with: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

echo "✅ Docker is installed"

# Check architecture
ARCH=$(uname -m)
echo "📋 Architecture: $ARCH"

if [ "$ARCH" != "aarch64" ] && [ "$ARCH" != "arm64" ]; then
    echo "⚠️  Warning: This system is not ARM64. These images are optimized for ARM64."
fi

echo ""
echo "Choose an option:"
echo ""
echo "1) wgen/acestream:arm64 (Recommended for Pi 5)"
echo "2) plaza24/acestream-arm64v8 (Older but stable)"
echo "3) Emulated x86_64 version (Fallback, slower)"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        COMPOSE_FILE="docker-compose-wgen.yml"
        IMAGE_NAME="wgen/acestream:arm64"
        ;;
    2)
        COMPOSE_FILE="docker-compose-plaza24.yml"
        IMAGE_NAME="plaza24/acestream-arm64v8:3.1.50-memory"
        ;;
    3)
        COMPOSE_FILE="docker-compose-emulated.yml"
        IMAGE_NAME="ghcr.io/martinbjeldbak/acestream-http-proxy:latest"
        echo ""
        echo "Setting up QEMU for emulation..."
        sudo apt-get update > /dev/null 2>&1
        sudo apt-get install -y qemu-user-static binfmt-support > /dev/null 2>&1
        docker run --rm --privileged multiarch/qemu-user-static --reset -p yes > /dev/null 2>&1
        echo "✅ QEMU configured"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Selected: $IMAGE_NAME"
echo "Using: $COMPOSE_FILE"
echo ""

# Check if file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "❌ File $COMPOSE_FILE not found!"
    echo "Make sure all docker-compose files are in the current directory."
    exit 1
fi

# Pull the image
echo "📥 Pulling Docker image..."
if [ $choice -eq 3 ]; then
    docker pull --platform linux/amd64 "$IMAGE_NAME"
else
    docker pull "$IMAGE_NAME"
fi

# Start the container
echo ""
echo "🚀 Starting Acestream..."
docker compose -f "$COMPOSE_FILE" up -d

# Wait a moment for container to start
sleep 3

# Check if container is running
if docker ps | grep -q acestream-proxy; then
    echo ""
    echo "================================================"
    echo "✅ Acestream is running!"
    echo "================================================"
    echo ""
    echo "Access your streams at:"
    echo "  HLS:     http://localhost:6878/ace/manifest.m3u8?id=STREAM_ID"
    echo "  MPEG-TS: http://localhost:6878/ace/getstream?id=STREAM_ID"
    echo ""
    echo "For remote access, use your Pi's IP address:"
    IP=$(hostname -I | awk '{print $1}')
    echo "  http://$IP:6878/ace/getstream?id=STREAM_ID"
    echo ""
    echo "Commands:"
    echo "  View logs:    docker logs -f acestream-proxy"
    echo "  Stop:         docker compose -f $COMPOSE_FILE down"
    echo "  Restart:      docker compose -f $COMPOSE_FILE restart"
    echo ""
else
    echo ""
    echo "❌ Container failed to start"
    echo "Check logs with: docker logs acestream-proxy"
    exit 1
fi
