#!/usr/bin/env python3
"""
AceStream Proxy Web Interface
Handles acestream:// links and converts them to playable stream URLs
"""

from flask import Flask, render_template, request, jsonify, redirect, send_file
from urllib.parse import urlencode, quote
import os
import sys
import re
import subprocess
import threading
import time
import uuid
from pathlib import Path

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configuration
ACESTREAM_PROXY_HOST = os.environ.get('ACESTREAM_PROXY_HOST', 'localhost')
ACESTREAM_PROXY_PORT = os.environ.get('ACESTREAM_PROXY_PORT', '6878')
WEB_PORT = os.environ.get('WEB_PORT', '5000')
WEB_HOST = os.environ.get('WEB_HOST', '0.0.0.0')

PROXY_URL = f'http://{ACESTREAM_PROXY_HOST}:{ACESTREAM_PROXY_PORT}'

# HLS Transcoding Configuration
HLS_SEGMENT_DIR = '/tmp/acestream-hls'
HLS_SEGMENT_DURATION = 2  # seconds
HLS_LIST_SIZE = 10  # number of segments to keep in playlist
TRANSCODE_THREADS = {}  # Track active transcoding threads by content_id

# Create HLS segment directory
Path(HLS_SEGMENT_DIR).mkdir(parents=True, exist_ok=True)


def extract_content_id(input_str):
    """Extract content ID from acestream:// link or return as-is if valid ID"""
    input_str = input_str.strip()

    # If it's an acestream link
    if input_str.startswith('acestream://'):
        content_id = input_str.replace('acestream://', '')
        if is_valid_content_id(content_id):
            return content_id
        return None

    # If it looks like a content ID (40 hex characters)
    if is_valid_content_id(input_str):
        return input_str.lower()

    return None


def is_valid_content_id(content_id):
    """Check if string is a valid 40-character hex content ID"""
    return bool(re.match(r'^[a-f0-9]{40}$', content_id.lower()))


def get_segment_dir(content_id):
    """Get the segment directory for a specific content ID"""
    return os.path.join(HLS_SEGMENT_DIR, content_id)


def start_transcoding(content_id):
    """Start ffmpeg transcoding from MPEG-TS to HLS in background thread"""
    if content_id in TRANSCODE_THREADS and TRANSCODE_THREADS[content_id].is_alive():
        return  # Already transcoding

    segment_dir = get_segment_dir(content_id)
    Path(segment_dir).mkdir(parents=True, exist_ok=True)

    def transcode_worker():
        try:
            # Build ffmpeg command to transcode MPEG-TS to HLS
            mpegts_url = f'{PROXY_URL}/ace/getstream?id={content_id}'
            manifest_path = os.path.join(segment_dir, 'manifest.m3u8')
            segment_pattern = os.path.join(segment_dir, 'segment-%05d.ts')

            # ffmpeg command to transcode MPEG-TS to HLS
            cmd = [
                'ffmpeg',
                '-i', mpegts_url,
                '-c:v', 'copy',  # Copy video codec (faster)
                '-c:a', 'aac',   # Transcode audio to AAC
                '-f', 'hls',
                '-hls_time', str(HLS_SEGMENT_DURATION),
                '-hls_list_size', str(HLS_LIST_SIZE),
                '-hls_flags', 'delete_segments',  # Delete old segments
                '-hls_segment_filename', segment_pattern,
                manifest_path
            ]

            # Run ffmpeg
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Wait for process to complete or error
            stdout, stderr = process.communicate()

        except Exception as e:
            print(f"Transcoding error for {content_id}: {e}")
        finally:
            # Clean up when done
            if content_id in TRANSCODE_THREADS:
                del TRANSCODE_THREADS[content_id]

    # Start transcoding in background thread
    thread = threading.Thread(target=transcode_worker, daemon=True)
    TRANSCODE_THREADS[content_id] = thread
    thread.start()


def get_hls_manifest(content_id):
    """Get the HLS manifest file for a content ID"""
    manifest_path = os.path.join(get_segment_dir(content_id), 'manifest.m3u8')

    if not os.path.exists(manifest_path):
        return None

    try:
        with open(manifest_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading manifest: {e}")
        return None


@app.route('/')
def index():
    """Serve the main web interface"""
    return open(os.path.join(os.path.dirname(__file__), 'index.html')).read()


@app.route('/api/convert', methods=['POST'])
def convert_link():
    """Convert acestream:// link to playable stream URL"""
    data = request.get_json()
    input_link = data.get('link', '').strip()

    if not input_link:
        return jsonify({'error': 'No link provided'}), 400

    content_id = extract_content_id(input_link)
    if not content_id:
        return jsonify({'error': 'Invalid acestream link or content ID'}), 400

    # Get the hostname from the request (browser can access this)
    request_host = request.host.split(':')[0]  # e.g., 'localhost' or '192.168.1.100'
    proxy_url_for_browser = f'http://{request_host}:6878'

    # Start transcoding in background
    start_transcoding(content_id)

    # Build URLs - transcoded HLS will be served via /stream/hls-live
    hls_transcoded_url = f'http://{request_host}:5000/stream/hls-live/{content_id}/manifest.m3u8'
    mpegts_url = f'{proxy_url_for_browser}/ace/getstream?id={content_id}'

    return jsonify({
        'content_id': content_id,
        'hls_transcoded_url': hls_transcoded_url,
        'mpegts_url': mpegts_url,
        'proxy_base': proxy_url_for_browser
    })


@app.route('/stream/hls-live/<content_id>/manifest.m3u8')
def stream_hls_live_manifest(content_id):
    """Serve transcoded HLS manifest"""
    if not is_valid_content_id(content_id):
        return jsonify({'error': 'Invalid content ID'}), 400

    # Get the manifest content
    manifest = get_hls_manifest(content_id)

    if manifest is None:
        # Manifest not ready yet, return a waiting response
        return '#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:2\n', 200, {'Content-Type': 'application/vnd.apple.mpegurl'}

    # Rewrite segment paths to be relative to this endpoint
    # Replace relative paths with absolute paths
    segment_dir = get_segment_dir(content_id)
    modified_manifest = manifest

    return modified_manifest, 200, {'Content-Type': 'application/vnd.apple.mpegurl'}


@app.route('/stream/hls-live/<content_id>/segment-<segment_num>.ts')
def stream_hls_live_segment(content_id, segment_num):
    """Serve transcoded HLS segment file"""
    if not is_valid_content_id(content_id):
        return jsonify({'error': 'Invalid content ID'}), 400

    segment_path = os.path.join(get_segment_dir(content_id), f'segment-{segment_num}.ts')

    if not os.path.exists(segment_path):
        return jsonify({'error': 'Segment not found'}), 404

    try:
        return send_file(segment_path, mimetype='video/mp2t', as_attachment=False)
    except Exception as e:
        print(f"Error serving segment: {e}")
        return jsonify({'error': 'Error serving segment'}), 500


@app.route('/stream/hls/<content_id>')
def stream_hls(content_id):
    """Proxy HLS stream from AceStream proxy"""
    if not is_valid_content_id(content_id):
        return jsonify({'error': 'Invalid content ID'}), 400

    # Get the hostname from the request (browser can access this)
    request_host = request.host.split(':')[0]

    # Redirect to the proxy's HLS endpoint using browser-accessible hostname
    return redirect(f'http://{request_host}:6878/ace/manifest.m3u8?id={content_id}')


@app.route('/stream/mpegts/<content_id>')
def stream_mpegts(content_id):
    """Proxy MPEG-TS stream from AceStream proxy"""
    if not is_valid_content_id(content_id):
        return jsonify({'error': 'Invalid content ID'}), 400

    # Get the hostname from the request (browser can access this)
    request_host = request.host.split(':')[0]

    # Redirect to the proxy's MPEG-TS endpoint using browser-accessible hostname
    return redirect(f'http://{request_host}:6878/ace/getstream?id={content_id}')


@app.route('/play', methods=['GET'])
def play():
    """Redirect acestream:// links to player"""
    # Handle query parameter ?id=CONTENT_ID
    content_id = request.args.get('id')

    if content_id and is_valid_content_id(content_id):
        # Redirect to HLS stream with redirect back to web interface
        params = urlencode({
            'id': content_id,
            'return': request.host
        })
        return redirect(f'/?{params}')

    return redirect('/')


@app.route('/stream/<format_type>')
def stream_redirect(format_type):
    """Redirect to proxy stream endpoint"""
    content_id = request.args.get('id')

    if not content_id or not is_valid_content_id(content_id):
        return jsonify({'error': 'Invalid content ID'}), 400

    if format_type == 'hls':
        return redirect(f'{PROXY_URL}/ace/manifest.m3u8?id={content_id}')
    elif format_type == 'mpegts':
        return redirect(f'{PROXY_URL}/ace/getstream?id={content_id}')
    else:
        return jsonify({'error': 'Invalid format'}), 400


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'version': '1.0'})


@app.route('/api/proxy-health', methods=['GET'])
def proxy_health():
    """Check if the AceStream proxy is healthy (proxied through web interface)"""
    try:
        import urllib.request
        response = urllib.request.urlopen(f'{PROXY_URL}/webui/api/service?method=get_version', timeout=5)
        data = response.read().decode('utf-8')
        return jsonify({'status': 'ok', 'proxy_healthy': True})
    except Exception as e:
        return jsonify({'status': 'error', 'proxy_healthy': False, 'error': str(e)}), 503


@app.route('/info')
def info():
    """Get proxy server info"""
    return jsonify({
        'name': 'AceStream Proxy Web Interface',
        'version': '1.0',
        'proxy_host': ACESTREAM_PROXY_HOST,
        'proxy_port': ACESTREAM_PROXY_PORT,
        'proxy_url': PROXY_URL,
        'web_port': WEB_PORT
    })


if __name__ == '__main__':
    print(f"Starting AceStream Proxy Web Interface")
    print(f"Web Interface: http://0.0.0.0:{WEB_PORT}")
    print(f"AceStream Proxy: {PROXY_URL}")
    print()

    app.run(
        host=WEB_HOST,
        port=int(WEB_PORT),
        debug=False,
        threaded=True
    )
