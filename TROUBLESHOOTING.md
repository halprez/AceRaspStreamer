# AceStream Proxy Troubleshooting Guide

## Current Status of Configurations

### ✅ WORKING - QEMU Emulation (docker-compose-emulated.yml)
**Recommendation**: Use this if native ARM64 fails

**Pros:**
- Most reliable on Raspberry Pi 5
- Latest Acestream version (3.2.11)
- Minimal crashes
- Simple to get working

**Cons:**
- ~30% performance overhead from emulation
- Higher CPU/memory usage

**How to use:**
```bash
docker compose -f docker-compose-emulated.yml up -d
```

**Test it:**
```bash
curl http://localhost:6878/webui/api/service?method=get_version
```

---

### ⚠️ UNSTABLE - wgen/acestream:arm64 (docker-compose-wgen.yml)
**Status**: Native ARM64 but has crash loop issues

**Problem:**
- Engine process crashes every 30-40 seconds
- Despite crashes, HTTP proxy wrapper continues running
- API may not respond reliably

**Symptoms:**
```
acehttp.py # ERROR    Ace Stream died, respawned with pid XXX
acehttp.py # ERROR    Can't spawn Ace Stream!
```

**Why it fails:**
- Binary incompatibility or missing ARM64 libraries
- Memory/resource constraints
- Engine dependency issues

**What we tried:**
- Increasing memory limits from 2GB to 4GB ✅ (improved but not fixed)
- Adding health checks ✅ (added)
- Adding SHM memory ✅ (added)

**Current recommendation:**
Do not use unless you specifically want to investigate the ARM64 binary issue.

---

### ⚠️ CRASHES - plaza24/acestream-arm64v8 (docker-compose-plaza24.yml)
**Status**: Segmentation fault on Raspberry Pi 5

**Problem:**
- Container exits immediately with SIGSEGV (signal 11)
- Binary not compatible with Raspberry Pi 5 architecture

**Why it fails:**
- Different ARM64 variant or binary build issue
- Not compatible with your system

**Current recommendation:**
Do not use.

---

## Recommended Setup Path

### For Raspberry Pi 5:

**Option 1 (RECOMMENDED - Works Now):**
```bash
docker compose -f docker-compose-emulated.yml up -d
```
Use the QEMU emulation. It's proven to work reliably.

**Option 2 (If you want to experiment):**
Try the wgen setup, but be prepared to switch back:
```bash
docker compose -f docker-compose-wgen.yml up -d
# Wait 30 seconds, then monitor:
docker logs -f acestream-proxy
# If you see "Ace Stream died, respawned" repeatedly, switch to QEMU
docker compose -f docker-compose-wgen.yml down
docker compose -f docker-compose-emulated.yml up -d
```

---

## Common Issues & Solutions

### Issue: Container exits immediately
```bash
docker logs acestream-proxy
```
- If you see segmentation fault → Use QEMU setup
- If you see engine crashes → Use QEMU setup

### Issue: Port 6878 already in use
```bash
sudo lsof -i :6878
# Kill the process:
sudo kill -9 <PID>
```

### Issue: API not responding
```bash
# Check container is running:
docker ps | grep acestream-proxy

# Check logs:
docker logs acestream-proxy

# If wgen image: expect engine crashes, switch to QEMU
# If QEMU: wait 60+ seconds for startup (it's slow)
```

### Issue: Slow performance with QEMU
This is expected - emulation adds ~30% overhead. Benefits:
- Reliability > Performance for a proxy server
- Sufficient for most streaming use cases
- Better than a completely non-functional native image

### Issue: Memory limits not working
```
Your kernel does not support memory limit capabilities
```
This is a cgroup warning and can be safely ignored on Docker.

---

## Performance Metrics

| Configuration | Status | Startup Time | CPU Usage | Memory | Reliability |
|--|--|--|--|--|--|
| QEMU (Emulated) | ✅ Working | 60-120s | Medium | ~500MB | Excellent |
| wgen (Native ARM64) | ⚠️ Unstable | 15-30s | Low | ~300MB | Poor (crashes) |
| plaza24 (Native ARM64) | ❌ Broken | N/A | N/A | N/A | Fails immediately |

---

## Advanced Troubleshooting

### Monitoring Container Health
```bash
# Watch real-time status:
docker stats acestream-proxy

# Check healthcheck status:
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Engine Crash Loop (wgen)
The wgen image tries to auto-respawn the engine. To see what's happening:
```bash
# Increase verbosity (if image supports it):
docker logs -f acestream-proxy | grep -i error

# Check if it's library issues:
docker exec acestream-proxy ldd /opt/acestream/acestreamengine 2>&1 | grep "not found"
```

### Rebuilding with Custom Configuration
If you need to modify behavior, create a custom docker-compose:
```yaml
version: '3.8'
services:
  acestream:
    image: ghcr.io/martinbjeldbak/acestream-http-proxy:latest
    platform: linux/amd64
    ports:
      - "6878:6878"
    environment:
      - ALLOW_REMOTE_ACCESS=yes
      - TZ=Atlantic/Canary
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

---

## Testing Your Setup

### 1. Check if service is responding
```bash
curl http://localhost:6878/webui/api/service?method=get_version
```

Expected response:
```json
{"result": {"platform": "linux", "version": "3.2.11", "code": 3021100, "websocket_port": 43743}, "error": null}
```

### 2. Test with a stream
```bash
# Using curl to test HLS endpoint:
curl -I 'http://localhost:6878/ace/manifest.m3u8?id=YOUR_STREAM_ID'

# Using VLC:
vlc 'http://localhost:6878/ace/getstream?id=YOUR_STREAM_ID'
```

### 3. Check remote access
```bash
# From another device on your network:
curl http://YOUR_PI_IP:6878/webui/api/service?method=get_version

# Find your Pi's IP:
hostname -I
```

---

## Conclusion

**For Raspberry Pi 5:** Use `docker-compose-emulated.yml` (QEMU)

The QEMU setup has been tested and verified to work reliably. While it has ~30% performance overhead, it provides stable Acestream streaming without crashes.

If you want to run native ARM64, you may need to:
1. Debug the wgen binary's missing dependencies
2. Try building a custom ARM64 image
3. Use a different ARM64 Acestream distribution

But for immediate, working results: **Use QEMU.**

