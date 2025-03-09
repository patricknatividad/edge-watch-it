from flask import Flask, render_template, request, jsonify
import requests
import time
from threading import Thread, Event
from datetime import datetime
import os

app = Flask(__name__)

# Configuration
AUTH_ENDPOINT = os.getenv('AUTH_ENDPOINT', 'https://example.com/api/authenticate')
BEARER_TOKEN = None

monitoring_thread = None
stop_event = Event()
log = []

@app.route('/')
def index():
    """Render the main index page."""
    return render_template('index.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    """Authenticate user and return a token if successful."""
    #global BEARER_TOKEN
    #auth_details = {
    #    "username": request.form['username'],
    #    "password": request.form['password']
    #}
    #response = requests.post(AUTH_ENDPOINT, json=auth_details)
    #if response.status_code == 200:
    #    BEARER_TOKEN = response.json().get('token')
    #    return jsonify({'status': 'Authentication successful'}), 200
    #else:
    #    return jsonify({'status': 'Authentication failed', 'message': 'Invalid username or password'}), 401

    global BEARER_TOKEN
    # Mock credentials
    mock_username = "admin"
    mock_password = "password123"

    username = request.form['username']
    password = request.form['password']

    if username == mock_username and password == mock_password:
        BEARER_TOKEN = "dummy_token"  # Use a dummy token for testing
        return jsonify({'status': 'Authentication successful'}), 200
    else:
        return jsonify({'status': 'Authentication failed', 'message': 'Invalid username or password'}), 401

@app.route('/start_monitoring', methods=['POST'])
def start_monitoring():
    """Start monitoring the specified API endpoint."""
    global monitoring_thread, stop_event, log
    stop_event.set()
    stop_event = Event()
    log = []

    endpoint = request.form['endpoint']
    interval = int(request.form['interval'])

    def monitor():
        while not stop_event.is_set():
            try:
                headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
                response = requests.get(endpoint, headers=headers)
                response.raise_for_status()
                data = response.json()
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log.append({'time': timestamp, 'value': data})
                time.sleep(interval)
            except requests.RequestException as e:
                handle_monitoring_error(e)
            except Exception as e:
                handle_monitoring_error(e)

    monitoring_thread = Thread(target=monitor)
    monitoring_thread.start()
    return jsonify({'status': 'Monitoring started'}), 200

def handle_monitoring_error(error):
    """Handle errors that occur during monitoring."""
    print(f"Error: {error}")
    stop_event.set()

@app.route('/get_log', methods=['GET'])
def get_log():
    """Return the monitoring log."""
    return jsonify(log)

@app.route('/stop_monitoring', methods=['POST'])
def stop_monitoring():
    """Stop the monitoring process."""
    global stop_event
    stop_event.set()
    return jsonify({'status': 'Monitoring stopped'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
