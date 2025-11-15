# AceStream HTTP Proxy on ARM64 (Raspberry Pi 5)

Complete solution with **beautiful web interface** for easy stream link conversion! 🎬

---

## ⚡ Quick Start - RECOMMENDED SETUP

### Start Everything (Proxy + Web Interface)

```bash
# Start both AceStream proxy AND web interface in one command:
docker compose -f docker-compose-complete.yml up -d

# Wait 60 seconds for startup, then open in your browser:
open http://localhost:5000
```

### Access the Web Interface

**Local**: http://localhost:5000
**Remote**: http://YOUR_PI_IP:5000

### How to Use

1. **Paste an AceStream link** or content ID
2. **Click "Play Stream"**
3. **Copy the generated URL**
4. **Open in VLC, MPV, or your media player**

### Example Workflow

```
Input:  acestream://dd1e67078381739d14beca697356ab76d49d1a2d
        ↓
Output: http://localhost:6878/ace/getstream?id=dd1e67078381739d14beca697356ab76d49d1a2d
        ↓
Play in: VLC → File → Open Network Stream → Paste → Play
```

---

## 🌟 What's Included

### AceStream Proxy Service
- **Status**: ✅ Working and tested
- **Port**: 6878
- **Version**: 3.2.11 (latest)
- **Technology**: QEMU emulation (most reliable)
- **Stream Formats**: HLS (M3U8) and MPEG-TS

### Web Interface
- **Status**: ✅ Running
- **Port**: 5000
- **Framework**: Flask/Python
- **Features**:
  - ✅ Convert `acestream://` links to HTTP URLs
  - ✅ Beautiful, responsive UI
  - ✅ One-click copy to clipboard
  - ✅ Real-time proxy detection
  - ✅ Multiple stream format support
  - ✅ Mobile-friendly design
  - ✅ Health checks and monitoring

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[WEB_QUICK_START.md](WEB_QUICK_START.md)** | Quick reference for the web interface |
| **[WEB_INTERFACE.md](WEB_INTERFACE.md)** | Complete web interface documentation |
| **[INSTALLATION_COMPLETE.md](INSTALLATION_COMPLETE.md)** | Setup completion guide |
| **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** | Issues and solutions |
| **[QUICKSTART.md](QUICKSTART.md)** | Original installation guide |

---

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

## ✅ Status of Deployment Options

| Option | Status | Performance | Stability | Acestream | Recommendation |
|--------|--------|-------------|-----------|-----------|-----------------|
| **QEMU Emulation** | ✅ **WORKING** | ~30% overhead | Excellent | 3.2.11 | **Use this!** |
| **wgen/acestream:arm64** | ⚠️ **Crashes** | Native speed | Poor (crash loop) | Recent | Don't use |
| **plaza24/acestream-arm64v8** | ❌ **Broken** | Native speed | None (segfault) | 3.1.50 | Don't use |

### Why QEMU is Recommended
- ✅ **Tested and verified** working on Raspberry Pi 5
- ✅ **Latest Acestream** version (3.2.11)
- ✅ **Extremely stable** - no crashes or errors
- ✅ **Simple to set up** - works out of the box
- ⚠️ **Trade-off**: ~30% performance overhead (still sufficient for streaming)

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed technical analysis.

---

## 🔧 Useful Commands

### Start/Stop Services

```bash
# Start both proxy and web interface:
docker compose -f docker-compose-complete.yml up -d

# View logs:
docker compose -f docker-compose-complete.yml logs -f

# Stop everything:
docker compose -f docker-compose-complete.yml down

# Restart:
docker compose -f docker-compose-complete.yml restart
```

### Check System Status

```bash
# See running containers:
docker ps

# Monitor resource usage:
docker stats

# View proxy logs:
docker logs acestream-proxy

# View web interface logs:
docker logs acestream-web
```

### Test Services

```bash
# Test proxy health:
curl http://localhost:6878/webui/api/service?method=get_version

# Test web interface health:
curl http://localhost:5000/health

# Test web interface info:
curl http://localhost:5000/info
```

### Proxy Endpoints

```bash
# Stream via HLS (better for web/mobile):
http://localhost:6878/ace/manifest.m3u8?id=CONTENT_ID

# Stream via MPEG-TS (better for players):
http://localhost:6878/ace/getstream?id=CONTENT_ID

# WebUI API:
http://localhost:6878/webui/api/service?method=get_version
```

### Web Interface API

```bash
# Convert acestream link to playable URLs:
curl -X POST http://localhost:5000/api/convert \
  -H "Content-Type: application/json" \
  -d '{"link":"acestream://dd1e67078381739d14beca697356ab76d49d1a2d"}'

# Response includes both HLS and MPEG-TS URLs
```

---

## 🌐 Remote Access

To access from other devices on your network:

1. Find your Pi's IP address:
   ```bash
   hostname -I
   ```

2. Access web interface:
   ```
   http://YOUR_PI_IP:5000
   ```

3. Or access proxy directly:
   ```
   http://YOUR_PI_IP:6878/ace/getstream?id=STREAM_ID
   ```

---

## 📥 Installation Methods

### Method 1: Complete Setup (Recommended)
```bash
# Everything in one command
docker compose -f docker-compose-complete.yml up -d
```

### Method 2: Proxy Only
```bash
# Just the AceStream proxy
docker compose -f docker-compose-emulated.yml up -d
```

### Method 3: Interactive Setup
```bash
# Run the setup wizard
chmod +x setup.sh
./setup.sh
```

---

## Troubleshooting

### Web Interface Won't Load

```bash
# Check if the container is running:
docker ps | grep acestream-web

# Test the health endpoint:
curl http://localhost:5000/health

# Check logs:
docker logs acestream-web
```

### AceStream Proxy Not Responding

```bash
# Check if container is running:
docker ps | grep acestream-proxy

# Test the proxy:
curl http://localhost:6878/webui/api/service?method=get_version

# Check logs:
docker logs acestream-proxy
```

### "Link conversion failed"

- Make sure you're using a valid acestream:// link
- Content ID must be 40 hex characters
- Proxy must be running (check with curl)
- Check browser console for errors

### Port Already in Use

```bash
# Check what's using the port:
sudo lsof -i :5000    # for web interface
sudo lsof -i :6878    # for proxy

# Kill the process if needed:
sudo kill -9 <PID>
```

### Stream Won't Play

1. Verify content ID is valid (40 hex characters)
2. Try both HLS and MPEG-TS formats
3. Ensure media player supports the format
4. Check network connectivity
5. View proxy logs: `docker logs acestream-proxy`

### Performance Issues

- **QEMU overhead**: Expected ~30% CPU overhead (normal)
- **Network bandwidth**: Check internet speed
- **Cooling**: Ensure Pi has adequate cooling
- **Other services**: Close apps using network resources

### Need More Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed analysis
- Check [WEB_INTERFACE.md](WEB_INTERFACE.md) for web interface help
- View detailed logs: `docker compose logs -f`

---

## 📁 Project Structure

```
AceRaspStreamer/
├── docker-compose-complete.yml    # ⭐ Recommended: Proxy + Web Interface
├── docker-compose-emulated.yml    # Proxy only (QEMU)
├── docker-compose-wgen.yml        # Proxy only (native ARM64 - not recommended)
├── docker-compose-plaza24.yml     # Proxy only (native ARM64 - not recommended)
│
├── web/
│   ├── index.html                 # Beautiful web UI
│   ├── app.py                     # Flask backend
│   ├── Dockerfile                 # Container definition
│   └── requirements.txt            # Python dependencies
│
├── setup.sh                        # Interactive setup wizard
├── start-acestream.sh              # Proxy startup script
├── run.sh                          # Alternative startup
│
├── README.md                       # ⭐ This file
├── WEB_QUICK_START.md             # Quick reference for web interface
├── WEB_INTERFACE.md               # Complete web interface docs
├── TROUBLESHOOTING.md             # Detailed troubleshooting guide
├── INSTALLATION_COMPLETE.md       # Setup completion info
├── QUICKSTART.md                  # Original installation guide
│
└── acestream-data/                # AceStream cache/config (created at runtime)
```

---

## ✨ Features Summary

### AceStream Proxy
- ✅ Working on Raspberry Pi 5
- ✅ Latest Acestream 3.2.11
- ✅ QEMU emulation (most reliable)
- ✅ Health checks
- ✅ Auto-restart
- ✅ Data persistence

### Web Interface
- ✅ Beautiful, responsive design
- ✅ Convert acestream:// links to HTTP URLs
- ✅ Support for HLS and MPEG-TS formats
- ✅ One-click copy to clipboard
- ✅ Real-time proxy detection
- ✅ Mobile-friendly interface
- ✅ API endpoints for integration
- ✅ Docker container orchestration

---

## 🚀 Getting Started (Complete Walkthrough)

### 1. **Start the System**
```bash
docker compose -f docker-compose-complete.yml up -d
```

### 2. **Wait for Startup**
```bash
# Takes ~60-120 seconds
sleep 60
```

### 3. **Open Web Interface**
```bash
# Local:
open http://localhost:5000

# Remote (replace with your Pi's IP):
open http://192.168.1.100:5000
```

### 4. **Convert a Link**
- Paste acestream:// link into the form
- Click "Play Stream"
- Copy the generated URL

### 5. **Open in Media Player**
```bash
# VLC:
vlc "http://localhost:6878/ace/getstream?id=YOUR_ID"

# Or manually:
# VLC → File → Open Network Stream → Paste → Play
```

### 6. **Monitor System**
```bash
# View logs:
docker compose -f docker-compose-complete.yml logs -f

# Check stats:
docker stats
```

---

## 📞 Need Help?

1. **Quick questions?** → See [WEB_QUICK_START.md](WEB_QUICK_START.md)
2. **Setup issues?** → See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. **Web interface?** → See [WEB_INTERFACE.md](WEB_INTERFACE.md)
4. **Check logs** → `docker compose logs -f`

---

## 📝 License

This project is provided as-is for educational purposes.

---

## 🎬 Start Streaming!

Your AceStream proxy and web interface are ready to use. Open http://localhost:5000 and enjoy streaming! 🎉
