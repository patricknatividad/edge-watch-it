from flask import Flask, render_template, request, jsonify
import requests
import time
from threading import Thread, Event
from datetime import datetime
import os

app = Flask(__name__)

BEARER_TOKEN = None
EDGE_IP = None

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
    global BEARER_TOKEN
    global EDGE_IP
    
    EDGE_IP = request.form['ipAddress']

    auth_details = {
        "username": request.form['username'],
        "password": request.form['password']
    }
    AUTH_ENDPOINT = f"https://{EDGE_IP}/edge/api/v1/login/getauthtoken/profile"

    response = requests.post(AUTH_ENDPOINT, data=auth_details, verify=False)
    if response.status_code == 200:
        BEARER_TOKEN = response.json().get('accessToken')
        return jsonify({'status': 'Authentication successful', 'accessToken': BEARER_TOKEN}), 200
    else:
        #error_message = response.json().get('message', 'Unknown error')
        error_message = "ERROR: Authentication failed"
        
        return jsonify({'status': 'Authentication failed', 'message': error_message}), 401

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
                response = requests.get(endpoint, headers=headers, verify=False)
                response.raise_for_status()
                data = response.json()
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log.append({'time': timestamp, 'value': data})
                print(f"Monitoring result at {timestamp}: {data}")  # Alert the user of the result
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
