# Web Interface Quick Start

Your AceStream web interface is now running! Here's how to use it:

## Access the Interface

Open your browser and go to:
```
http://localhost:5000
```

Or from another device on your network:
```
http://YOUR_PI_IP:5000
```

(Find your Pi's IP with: `hostname -I`)

---

## How to Use

### 1. **Paste an AceStream Link**
- Copy an `acestream://` link from the web
- Paste it into the interface
- Or just paste the 40-character ID

### 2. **Click "Play Stream"**
- The interface will verify your proxy is working
- You'll get two stream URLs:
  - **HLS** (better for web/mobile)
  - **MPEG-TS** (better for desktop players)

### 3. **Open in Your Player**
- Copy one of the URLs
- Paste into **VLC**, **MPV**, or your favorite media player
- Press play!

---

## Example

### Input:
```
acestream://dd1e67078381739d14beca697356ab76d49d1a2d
```

### Output (HLS):
```
http://YOUR_PI_IP:6878/ace/manifest.m3u8?id=dd1e67078381739d14beca697356ab76d49d1a2d
```

### Open in VLC:
```
File → Open Network Stream → Paste URL → Play
```

---

## Using with VLC

### Desktop
```bash
# From command line:
vlc 'http://localhost:6878/ace/getstream?id=dd1e67078381739d14beca697356ab76d49d1a2d'

# Or manually:
# 1. Open VLC
# 2. File → Open Network Stream (Ctrl+N)
# 3. Paste the URL
# 4. Click Play
```

### Mobile (VLC for iOS/Android)
1. Open VLC app
2. Tap network icon
3. Paste stream URL
4. Tap play

---

## Architecture

```
Your Browser (http://localhost:5000)
        ↓
   Web Interface (Flask)
   - Converts acestream:// links
   - Generates stream URLs
        ↓
   AceStream Proxy (Port 6878)
   - /ace/manifest.m3u8?id=...
   - /ace/getstream?id=...
        ↓
   Your Media Player
   - VLC, MPV, Browser, etc.
```

---

## System Status

Your system is running with:

✅ **AceStream Proxy** (port 6878)
- Latest version (3.2.11)
- QEMU emulation (most reliable)
- Status: Running

✅ **Web Interface** (port 5000)
- Beautiful UI for link conversion
- Real-time proxy detection
- Copy-to-clipboard support
- Status: Running

---

## Troubleshooting

### "Proxy not responding"
```bash
# Check if proxy is running:
docker ps | grep acestream-proxy

# Verify port 6878:
curl http://localhost:6878/webui/api/service?method=get_version
```

### "Web interface won't load"
```bash
# Check if web container is running:
docker ps | grep acestream-web

# Test health:
curl http://localhost:5000/health
```

### "Stream won't play"
1. Make sure content ID is valid (40 hex characters)
2. Try both HLS and MPEG-TS formats
3. Ensure media player supports the format
4. Check: `docker logs acestream-proxy` for errors

---

## Advanced: Protocol Handler

To make `acestream://` links open automatically in the web interface (optional):

### Chrome/Edge
1. Settings → Advanced → Site settings
2. Look for "Protocols"
3. Allow this site to handle `acestream://`

### Firefox
1. Go to `about:config`
2. Set `browser.link.open-newwindow.restriction = 0`

---

## Next Steps

- **Share your Pi's IP** with family/friends
- **Bookmark this page** for easy access
- **Use different stream formats** to find what works best
- **Monitor performance** with `docker stats`

---

## Full Documentation

For detailed setup, configuration, and troubleshooting, see:
- [WEB_INTERFACE.md](WEB_INTERFACE.md) - Complete guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Proxy issues
- [README.md](README.md) - Installation

---

## Files Included

```
web/
├── index.html           # Beautiful web interface
├── app.py              # Flask backend
├── Dockerfile          # Container definition
└── requirements.txt    # Python dependencies

docker-compose-complete.yml  # Start everything in one command
```

---

## Start/Stop Commands

```bash
# Start everything:
docker compose -f docker-compose-complete.yml up -d

# View logs:
docker compose -f docker-compose-complete.yml logs -f

# Stop everything:
docker compose -f docker-compose-complete.yml down

# Restart:
docker compose -f docker-compose-complete.yml restart
```

---

## Support

If you need help:
1. Check logs: `docker compose logs -f`
2. Read [WEB_INTERFACE.md](WEB_INTERFACE.md) for advanced setup
3. Verify proxy: `curl http://localhost:6878/webui/api/service?method=get_version`

Happy streaming! 🎬

