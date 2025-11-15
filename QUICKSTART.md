# Acestream on Raspberry Pi 5 - Quick Start

## 🚀 Super Quick Start (WORKING SOLUTION)

For Raspberry Pi 5, use QEMU emulation - it's the most reliable:

```bash
# Use QEMU emulation (most stable):
docker compose -f docker-compose-emulated.yml up -d

# Verify it's working (wait 60 seconds for startup):
curl http://localhost:6878/webui/api/service?method=get_version
```

**Alternative approaches:**

```bash
# Option 1: Try native ARM64 wgen (faster but may crash):
docker run -d -p 6878:6878 --name acestream wgen/acestream:arm64

# Option 2: Alternative ARM64 (very stable but older):
docker run -d -p 6878:6878 -e ALLOW_REMOTE_ACCESS=yes plaza24/acestream-arm64v8:3.1.50-memory

# Option 3: Emulated x86_64 via QEMU (slower but most reliable) ✅ RECOMMENDED
docker run -d --platform linux/amd64 -p 6878:6878 ghcr.io/martinbjeldbak/acestream-http-proxy:latest
```

⚠️ **Known Issues:**
- **wgen/acestream:arm64**: Engine crashes every 30 seconds (use QEMU instead)
- **plaza24/acestream-arm64v8**: Segmentation fault on Pi 5 (use QEMU instead)
- **QEMU emulation**: ~30% slower but stable and reliable ✅

## 📦 Recommended Setup (with docker-compose)

**Use the automated setup script:**

```bash
chmod +x setup.sh
./setup.sh
```

The script will guide you through choosing the best option for your Pi 5.

**Or manually with docker-compose:**

```bash
# For Raspberry Pi 5 - use native ARM64
docker compose -f docker-compose-wgen.yml up -d

# Check it's running
docker logs acestream-proxy
```

## 🎬 Usage

Once running, access streams with:

```bash
# HLS format (better for most players)
http://localhost:6878/ace/manifest.m3u8?id=YOUR_STREAM_ID

# MPEG-TS format
http://localhost:6878/ace/getstream?id=YOUR_STREAM_ID
```

**Example with VLC:**
```bash
vlc http://localhost:6878/ace/getstream?id=dd1e67078381739d14beca697356ab76d49d1a2d
```

## 📱 Remote Access

To access from other devices (phones, tablets, other computers):

1. Use your Pi's IP address instead of localhost
2. Make sure `ALLOW_REMOTE_ACCESS=yes` is set (it is in the provided configs)

```bash
# Find your Pi's IP
hostname -I

# Access from another device
http://192.168.1.XXX:6878/ace/getstream?id=STREAM_ID
```

## 🛠️ Files Included

- **setup.sh** - Interactive setup script (easiest)
- **docker-compose-wgen.yml** - Native ARM64 (recommended for Pi 5)
- **docker-compose-plaza24.yml** - Alternative ARM64 (older version, very stable)
- **docker-compose-emulated.yml** - Emulated x86_64 (fallback option)
- **README-ARM64-SIMPLE.md** - Detailed documentation

## ✅ Which One to Use?

**Raspberry Pi 5**: Start with `wgen/acestream:arm64` (docker-compose-wgen.yml)

It's native ARM64, performs well, and uses a recent Acestream version.

## 🔧 Troubleshooting

**Container won't start?**
```bash
docker logs acestream-proxy
```

**Port already in use?**
```bash
# Change the port in docker-compose.yml:
ports:
  - "8878:6878"  # Use 8878 instead
```

**Performance issues?**
- Make sure you're using a native ARM64 image, not the emulated one
- Ensure your Pi has adequate cooling
- Check your internet connection speed

## 📊 Performance Comparison

| Method | Performance | Complexity | Best For |
|--------|-------------|-----------|----------|
| **wgen/acestream:arm64** | ⭐⭐⭐⭐⭐ | Easy | Pi 5 (recommended) |
| **plaza24 ARM64** | ⭐⭐⭐⭐⭐ | Easy | Older Pi, stability |
| **Emulated x86_64** | ⭐⭐⭐ | Medium | Fallback only |

## 🎯 Next Steps

1. Run `./setup.sh` or choose a docker-compose file
2. Test with a stream: `vlc http://localhost:6878/ace/getstream?id=YOUR_ID`
3. For remote access, share your Pi's IP with other devices

That's it! The native ARM64 containers make this really simple.
