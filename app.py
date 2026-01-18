from flask import Flask, render_template, jsonify, request, redirect
from flask_cors import CORS
import json
import os
from functools import wraps

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# API Configuration
PUBLIC_KEY = "NZ_PUB_7f9a2e8c4b6d1a5f3e0c9b7a4d2f8e1c"
SECRET_KEY_FILE = "static/data/secret_key.txt"


def load_json(filename):
    """Load JSON data from file"""
    filepath = os.path.join('static/data', filename)
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_secret_key():
    """Get secret key from file"""
    if os.path.exists(SECRET_KEY_FILE):
        with open(SECRET_KEY_FILE, 'r') as f:
            return f.read().strip()
    return None


def require_api_keys(f):
    """Decorator to require API keys"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        public_key = request.args.get('public_key') or request.headers.get('X-Public-Key')
        secret_key = request.args.get('secret_key') or request.headers.get('X-Secret-Key')

        stored_secret = get_secret_key()

        if not public_key or not secret_key:
            return jsonify({
                'error': 'Missing API keys',
                'message': 'Both public_key and secret_key are required'
            }), 401

        if public_key != PUBLIC_KEY or secret_key != stored_secret:
            return jsonify({
                'error': 'Invalid API keys',
                'message': 'The provided API keys are invalid'
            }), 403

        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/api/health')
def api_health():
    return jsonify({
        'status': 'healthy',
        'service': 'Netzone API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'v2rays': '/api/v2rays (requires authentication)'
        }
    }), 200


@app.route('/api/v2rays')
@require_api_keys
def api_v2rays():
    try:
        v2rays = load_json('free_v2rays.json')
        return jsonify({
            'success': True,
            'count': len(v2rays.get('vpn_configs', [])),
            'data': v2rays
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/apps')
def api_apps():
    try:
        apps = load_json('apps.json')
        return jsonify({
            'success': True,
            'count': len(apps.get('apps', [])),
            'data': apps
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/whatsapp')
def whatsapp():
    return redirect("https://chat.whatsapp.com/Hre9DcY71UvC32oMVwwUrE", code=302)


@app.route('/discord')
def discord():
    return redirect("https://discord.gg/DhPZ8uMv4v", code=302)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('404.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
