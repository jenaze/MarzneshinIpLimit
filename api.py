from flask import Flask, request, jsonify
import json
import os
from datetime import datetime, timedelta, UTC
from jose import JWTError, jwt
from functools import wraps

# Constants
CONFIG_FILE = 'config.json'
LOG_FILE = 'cronjob_log.log'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

app = Flask(__name__)

# Helper Functions
def load_config():
    """Load configuration from config file"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load config once to avoid repeated file reads
_config = load_config()
SECRET_KEY = _config["SECRET_KEY"]
API_USERNAME = _config["API_USERNAME"]
API_PASSWORD = _config["API_PASSWORD"]

def save_config(config):
    """Save configuration to config file"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def log(message):
    """Write log to file"""
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{message}\n")

# JWT Functions
def create_access_token(username):
    """Create access token for user"""
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token):
    """Verify access token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

def token_required(f):
    """Decorator to verify token in requests"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        try:
            token = token.split(" ")[1]  # Bearer token
        except IndexError:
            return jsonify({"error": "Invalid token format"}), 401
        username = verify_token(token)
        if not username:
            return jsonify({"error": "Invalid or expired token"}), 401
        return f(username, *args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
def login():
    """User login and access token retrieval"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Verify user credentials
    if username == API_USERNAME and password == API_PASSWORD:
        token = create_access_token(username)
        return jsonify({"access_token": token, "token_type": "bearer"})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/update_special_limit', methods=['POST'])
@token_required
def update_special_limit(username):
    """Update special limit for user"""
    if username != API_USERNAME:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    user = data.get('user')
    limit = data.get('limit')

    if not user or not isinstance(limit, int):
        return jsonify({'error': 'Invalid input: user and limit (integer) are required'}), 400
    
    if limit < 0:
        return jsonify({'error': 'Limit must be a positive number'}), 400

    config = load_config()

    # Check if user exists in SPECIAL_LIMIT
    special_limit = config.get('SPECIAL_LIMIT', [])
    for i, (existing_user, existing_limit) in enumerate(special_limit):
        if existing_user == user:
            special_limit[i] = [user, limit]
            config['SPECIAL_LIMIT'] = special_limit
            save_config(config)
            return jsonify({'status': 'updated', 'user': user, 'limit': limit}), 200

    # If user doesn't exist, add it
    special_limit.append([user, limit])
    config['SPECIAL_LIMIT'] = special_limit
    save_config(config)
    return jsonify({'status': 'added', 'user': user, 'limit': limit}), 201

if __name__ == '__main__':
    app.run(host="0.0.0.0" ,port=int(os.environ.get('PORT', 6284)))
