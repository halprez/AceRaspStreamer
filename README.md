# Acestream HTTP Proxy on ARM64 (Raspberry Pi 5)

## Ready-to-Use ARM64 Containers

Several ARM64 Acestream containers already exist. Here are your best options:

---

## Option 1: wgen/acestream (Recommended for Raspberry Pi 5)

This is a native ARM64 build specifically for modern ARM devices.

### Quick Start

```bash
docker run -d \
  --name acestream \
  -p 6878:6878 \
  wgen/acestream:arm64
```

### With docker-compose

```yaml
version: '3.8'

services:
  acestream:
    image: wgen/acestream:arm64
    container_name: acestream
    ports:
      - "6878:6878"
    restart: unless-stopped
    volumes:
      - ./acestream-data:/root/.ACEStream
```

### Usage

Access streams at:
- **HLS**: `http://localhost:6878/ace/manifest.m3u8?id=STREAM_ID`
- **MPEG-TS**: `http://localhost:6878/ace/getstream?id=STREAM_ID`

Replace `STREAM_ID` with your Acestream content ID.

---

## Option 2: plaza24/acestream-arm64v8

Community-built ARM64 image with good stability.

### Quick Start

```bash
docker run -d \
  --name acestream \
  -p 6878:6878 \
  -e ALLOW_REMOTE_ACCESS=yes \
  plaza24/acestream-arm64v8:3.1.50-memory
```

### With docker-compose

```yaml
version: '3.8'

services:
  acestream:
    image: plaza24/acestream-arm64v8:3.1.50-memory
    container_name: acestream
    ports:
      - "6878:6878"
    environment:
      - HTTP_PORT=6878
      - ALLOW_REMOTE_ACCESS=yes
    restart: unless-stopped
    volumes:
      - ./acestream-data:/root/.ACEStream
```

**Note**: This uses an older Acestream version (3.1.50) but is proven stable.

---

## Option 3: QEMU Emulation (Original x86_64 Container)

If native ARM64 containers don't work well, use QEMU to run the original x86_64 image:

### Prerequisites

```bash
# Install QEMU support
sudo apt-get update
sudo apt-get install -y qemu-user-static binfmt-support
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```

### Run Original Container

```bash
docker run -d \
  --platform linux/amd64 \
  --name acestream \
  -p 6878:6878 \
  -e ALLOW_REMOTE_ACCESS=yes \
  ghcr.io/martinbjeldbak/acestream-http-proxy:latest
```

### With docker-compose

```yaml
version: '3.8'

services:
  acestream:
    image: ghcr.io/martinbjeldbak/acestream-http-proxy:latest
    platform: linux/amd64  # Force x86_64 emulation
    container_name: acestream
    ports:
      - "6878:6878"
    environment:
      - ALLOW_REMOTE_ACCESS=yes
    restart: unless-stopped
```

**Pros**: Uses latest official-ish image  
**Cons**: Slower performance due to emulation overhead

---

## Testing Your Setup

Once the container is running, test it:

```bash
# Check if the engine is responding
curl http://localhost:6878/webui/api/service?method=get_version

# Test with a sample stream (replace STREAM_ID)
vlc http://localhost:6878/ace/getstream?id=YOUR_STREAM_ID
```

---

## Comparison

| Container | Performance | Acestream Version | Stability | Best For |
|-----------|------------|-------------------|-----------|----------|
| **wgen/acestream:arm64** | Native | Recent | Good | Pi 5 (recommended) |
| **plaza24/acestream-arm64v8** | Native | 3.1.50 (older) | Very stable | Older Pi models |
| **QEMU emulation** | ~70% slower | Latest | Good | Fallback option |

---

## Remote Access

To access from other devices on your network:

1. Set `ALLOW_REMOTE_ACCESS=yes` in your docker-compose or run command
2. Use your Raspberry Pi's IP address instead of localhost:
   ```
   http://192.168.1.XXX:6878/ace/getstream?id=STREAM_ID
   ```

---

## Troubleshooting

### Container exits immediately
```bash
# Check logs
docker logs acestream

# Try running in foreground to see errors
docker run --rm -it wgen/acestream:arm64
```

### Port already in use
```bash
# Check what's using port 6878
sudo ss -tulpn | grep 6878

# Use a different port
docker run -d -p 8878:6878 wgen/acestream:arm64
```

### Performance issues
- If using QEMU emulation, try native ARM64 images instead
- Ensure Raspberry Pi has adequate cooling
- Check network bandwidth isn't the bottleneck

---

## Which Option Should You Choose?

**For Raspberry Pi 5**: Start with **wgen/acestream:arm64** (Option 1)

**If Option 1 doesn't work**: Try **plaza24/acestream-arm64v8** (Option 2)

**If native images have issues**: Fall back to **QEMU emulation** (Option 3)
