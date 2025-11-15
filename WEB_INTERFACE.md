# AceStream Web Interface - acestream:// Link Handler

A modern web interface to convert `acestream://` links into playable HTTP streams, allowing you to click on AceStream links and watch them directly in your browser or media player.

## Features

✅ **Easy Link Conversion** - Paste acestream:// links and get playable URLs
✅ **Multiple Formats** - HLS (M3U8) and MPEG-TS stream options
✅ **Beautiful UI** - Modern, responsive web interface
✅ **Protocol Handler** - Register as default handler for acestream:// links
✅ **Copy to Clipboard** - One-click copy of generated URLs
✅ **Real-time Proxy Detection** - Automatically detects your proxy server

---

## Quick Start

### Option 1: Using Docker Compose (Easiest)

```bash
# Start both AceStream proxy AND web interface
docker compose -f docker-compose-complete.yml up -d

# Access the interface
open http://localhost:5000
```

### Option 2: Separate Components

```bash
# Start just the AceStream proxy (if not already running)
docker compose -f docker-compose-emulated.yml up -d

# Start the web interface (requires Python 3.7+)
cd web
pip install Flask
python3 app.py

# Access the interface
open http://localhost:5000
```

---

## How to Use

### 1. Open the Web Interface
Navigate to: `http://localhost:5000` (or your server's IP)

### 2. Paste an AceStream Link
You'll see a clean interface where you can:
- Paste an `acestream://` link
- Or paste just the 40-character content ID

### 3. Click "Play Stream"
The interface will:
- Verify the AceStream proxy is running
- Generate HLS and MPEG-TS stream URLs
- Display both formats for copying

### 4. Open in Your Player
Copy one of the generated URLs and open it in:
- **VLC Player** (Desktop) - Best compatibility
- **MPV** - Lightweight, excellent performance
- **Web Browser** - HLS format works in most browsers
- **Mobile Apps** - If they support HTTP streaming

---

## Input Formats

The web interface accepts two input formats:

### Format 1: Full AceStream Link
```
acestream://dd1e67078381739d14beca697356ab76d49d1a2d
```

### Format 2: Content ID Only
```
dd1e67078381739d14beca697356ab76d49d1a2d
```

Both will produce the same playable URLs.

---

## Output Formats

### HLS Format (M3U8)
```
http://YOUR_PROXY_IP:6878/ace/manifest.m3u8?id=dd1e67078381739d14beca697356ab76d49d1a2d
```
**Best for:** Web browsers, mobile apps, cross-platform compatibility

### MPEG-TS Format
```
http://YOUR_PROXY_IP:6878/ace/getstream?id=dd1e67078381739d14beca697356ab76d49d1a2d
```
**Best for:** Desktop players (VLC, MPV), low-latency streaming

---

## Protocol Handler Setup (Optional)

Make `acestream://` links open directly in your web interface.

### Chrome/Edge
1. Visit your web interface: `http://localhost:5000`
2. Settings → Advanced → Site settings
3. Look for "Additional permissions" section
4. Allow this site to handle `acestream://` protocol

### Firefox
1. Go to `about:config`
2. Search for: `browser.link.open-newwindow.restriction`
3. Set value to `0`
4. Visit your web interface and confirm protocol handler

### Safari
1. Preferences → Websites
2. Look for "Custom settings" or "Protocols"
3. Add your web interface to handle `acestream://`

### Browser Extensions
For advanced protocol handling, use:
- **Acestream Link Handler** (Chrome Web Store)
- **AceStream Redirector** (Firefox Add-ons)

---

## Using with VLC Media Player

### Desktop (Windows, Mac, Linux)

```bash
# Method 1: Direct URL
vlc 'http://YOUR_IP:6878/ace/getstream?id=CONTENT_ID'

# Method 2: From command line
echo "http://YOUR_IP:6878/ace/getstream?id=dd1e67078381739d14beca697356ab76d49d1a2d" | xclip
# Then paste into VLC: Ctrl+N (New Stream) → Paste → Play
```

### Mobile (VLC for iOS/Android)

1. Open VLC app
2. Tap the network icon (top left)
3. Paste your stream URL
4. Tap play

---

## Configuration

### Environment Variables

```bash
# AceStream proxy connection
ACESTREAM_PROXY_HOST=localhost      # Or your Raspberry Pi IP
ACESTREAM_PROXY_PORT=6878           # Default AceStream port

# Web interface settings
WEB_HOST=0.0.0.0                    # Listen on all interfaces
WEB_PORT=5000                       # Port for web interface
FLASK_ENV=production                # Set to development for debug
```

### With Docker

```bash
# Set proxy host to your Pi's IP for remote access
docker run -e ACESTREAM_PROXY_HOST=192.168.1.100 \
           -p 5000:5000 \
           acestream-web:latest
```

---

## API Endpoints

### GET `/`
Returns the web interface HTML

### POST `/api/convert`
Convert acestream link to stream URLs

**Request:**
```json
{
  "link": "acestream://dd1e67078381739d14beca697356ab76d49d1a2d"
}
```

**Response:**
```json
{
  "content_id": "dd1e67078381739d14beca697356ab76d49d1a2d",
  "hls_url": "http://localhost:6878/ace/manifest.m3u8?id=...",
  "mpegts_url": "http://localhost:6878/ace/getstream?id=...",
  "proxy_base": "http://localhost:6878"
}
```

### GET `/play?id=CONTENT_ID`
Redirect to play stream

### GET `/health`
Health check endpoint

### GET `/info`
Get proxy server information

---

## Troubleshooting

### "Proxy not responding"
- Check AceStream proxy is running: `docker ps | grep acestream-proxy`
- Verify port 6878 is accessible
- Check logs: `docker logs acestream-proxy`

### "Invalid content ID"
- Ensure you're using a valid 40-character hex string
- Example valid ID: `dd1e67078381739d14beca697356ab76d49d1a2d`
- Don't include `acestream://` if already entered

### Web interface not accessible
- Check web container is running: `docker ps | grep acestream-web`
- Try `curl http://localhost:5000/health`
- Ensure port 5000 isn't already in use

### Stream won't play
- Verify content is available on the AceStream network
- Try both HLS and MPEG-TS formats
- Check your media player supports the format
- Ensure network connectivity to the AceStream network

### Slow streaming
- Normal for QEMU emulation (~30% overhead expected)
- Check network bandwidth: `speedtest-cli`
- Try MPEG-TS instead of HLS for lower latency
- Close other applications using network

---

## Advanced Usage

### Using with systemd

Create `/etc/systemd/system/acestream-web.service`:

```ini
[Unit]
Description=AceStream Web Interface
After=docker.service
Requires=docker.service

[Service]
Type=simple
ExecStart=/usr/bin/docker compose -f /path/to/docker-compose-complete.yml up
ExecStop=/usr/bin/docker compose -f /path/to/docker-compose-complete.yml down
Restart=always

[Install]
WantedBy=multi-user.target
```

Start with:
```bash
sudo systemctl start acestream-web
sudo systemctl enable acestream-web
```

### Using with Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name acestream.example.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;
    }

    location /ace/ {
        proxy_pass http://localhost:6878;
        proxy_buffering off;
        proxy_cache_bypass $http_pragma $http_authorization;
    }
}
```

### Custom Branding

Edit `index.html` to customize:
- Title and colors (modify CSS)
- Help text and instructions
- Logo or branding

---

## Performance Tips

1. **Use MPEG-TS for Low Latency**
   - Better for live streams
   - Lower CPU overhead than HLS

2. **Use HLS for Compatibility**
   - Works in web browsers
   - Better for mobile devices
   - More forgiving with network issues

3. **Local Access**
   - Much faster on same network
   - Consider wired connection for stability

4. **VLC Settings**
   - Tools → Preferences → Input/Codecs → Network caching: 1000-5000ms
   - Tools → Preferences → Video → Output module: Hardware acceleration if available

---

## Architecture

```
┌─────────────────────────────────────┐
│  User's Browser                     │
│  http://localhost:5000              │
└────────────────┬────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────┐
│  Web Interface (Flask)               │
│  • Accepts acestream:// links       │
│  • Generates proxy URLs             │
│  • Beautiful UI                     │
└────────────────┬────────────────────┘
                 │
    ┌────────────┘
    │
    ↓
┌─────────────────────────────────────┐
│  AceStream Proxy (Docker)           │
│  Port 6878                          │
│  • /ace/manifest.m3u8?id=...       │
│  • /ace/getstream?id=...            │
└────────────────┬────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────┐
│  Media Player                       │
│  VLC, MPV, Browser, Mobile App      │
└─────────────────────────────────────┘
```

---

## File Structure

```
web/
├── index.html       # Web interface (HTML + CSS + JavaScript)
├── app.py          # Flask backend
├── Dockerfile      # Container definition
└── requirements.txt # Python dependencies (optional)
```

---

## Security Considerations

⚠️ **Important:**
- This interface should be **behind a firewall** on public networks
- Don't expose port 5000 to the internet without authentication
- Consider using HTTPS in production
- Validate all user inputs (already done in code)

For production deployments:
1. Use Nginx/Apache as reverse proxy with HTTPS
2. Add authentication (basic auth, OAuth)
3. Use firewall rules to restrict access
4. Monitor access logs

---

## Support

If you encounter issues:

1. Check the TROUBLESHOOTING.md guide
2. Review Docker logs: `docker compose logs -f`
3. Verify proxy is running: `curl http://localhost:6878/webui/api/service?method=get_version`
4. Test web interface: `curl http://localhost:5000/health`

---

## License

Same as AceRaspStreamer project

