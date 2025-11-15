#!/usr/bin/env python3
"""
AceStream Proxy Web Interface
Handles acestream:// links and converts them to playable stream URLs
"""

from flask import Flask, render_template, request, jsonify, redirect
from urllib.parse import urlencode, quote
import os
import sys
import re

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configuration
ACESTREAM_PROXY_HOST = os.environ.get('ACESTREAM_PROXY_HOST', 'localhost')
ACESTREAM_PROXY_PORT = os.environ.get('ACESTREAM_PROXY_PORT', '6878')
WEB_PORT = os.environ.get('WEB_PORT', '5000')
WEB_HOST = os.environ.get('WEB_HOST', '0.0.0.0')

PROXY_URL = f'http://{ACESTREAM_PROXY_HOST}:{ACESTREAM_PROXY_PORT}'


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

    # Build MPEG-TS URL - the only reliably working format
    mpegts_url = f'{proxy_url_for_browser}/ace/getstream?id={content_id}'

    return jsonify({
        'content_id': content_id,
        'mpegts_url': mpegts_url,
        'proxy_base': proxy_url_for_browser
    })


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
