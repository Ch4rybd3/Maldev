#!/usr/bin/env python3

import os
import sys
import glob
import argparse
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from datetime import datetime
import binascii

# Configuration
LOG_DIR = "logs"
PRIVATE_KEY_FILE = "RSA/private_key.pem"  # Assurez-vous que ce fichier existe avec la clé privée correspondante

def load_private_key():
    """Charge la clé privée RSA depuis le fichier."""
    try:
        with open(PRIVATE_KEY_FILE, 'r') as f:
            private_key_pem = f.read()
        return RSA.import_key(private_key_pem)
    except Exception as e:
        print(f"[-] Erreur lors du chargement de la clé privée: {e}")
        sys.exit(1)

def decrypt_aes_key(encrypted_key_hex, private_key):
    """Déchiffre une clé AES avec la clé privée RSA."""
    try:
        # Convertir la chaîne hexadécimale en bytes
        encrypted_key = binascii.unhexlify(encrypted_key_hex)
        
        # Déchiffrer avec RSA-OAEP
        cipher_rsa = PKCS1_OAEP.new(private_key)
        decrypted_key = cipher_rsa.decrypt(encrypted_key)
        
        return decrypted_key.hex()
    except binascii.Error:
        return "[Format de clé hexadécimale invalide]"
    except Exception as e:
        return f"[Erreur de déchiffrement: {e}]"

def find_logs_by_hostname(hostname):
    """Trouve tous les fichiers de log correspondant au hostname."""
    log_pattern = os.path.join(LOG_DIR, f"log_{hostname}_*.log")
    return glob.glob(log_pattern)

def parse_log_file(log_file, private_key):
    """Parse un fichier de log et déchiffre la clé AES."""
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        log_data = {}
        for line in lines:
            if ': ' in line:
                key, value = line.strip().split(": ", 1)
                log_data[key] = value
        
        # Extraction du timestamp pour l'affichage formaté
        try:
            timestamp = datetime.fromisoformat(log_data.get("Timestamp", ""))
            formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatted_timestamp = log_data.get("Timestamp", "Inconnu")
        
        # Déchiffrer la clé AES
        encrypted_aes_key = log_data.get("AES Key", "")
        decrypted_aes_key = decrypt_aes_key(encrypted_aes_key, private_key)
        
        return {
            "filename": os.path.basename(log_file),
            "hostname": log_data.get("Hostname", "Inconnu"),
            "timestamp": formatted_timestamp,
            "encrypted_key": encrypted_aes_key,
            "decrypted_key": decrypted_aes_key
        }
    except Exception as e:
        print(f"[-] Erreur lors de l'analyse du fichier {log_file}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Déchiffre les clés AES stockées dans les logs.")
    parser.add_argument("hostname", help="Le nom d'hôte à rechercher dans les logs")
    parser.add_argument("-a", "--all", action="store_true", help="Afficher tous les logs pour ce hostname")
    parser.add_argument("-l", "--latest", action="store_true", help="Afficher uniquement le dernier log (par défaut)")
    args = parser.parse_args()
    
    # Si ni --all ni --latest n'est spécifié, on utilise --latest par défaut
    if not args.all and not args.latest:
        args.latest = True
    
    # Charger la clé privée
    private_key = load_private_key()
    
    # Trouver les logs correspondant au hostname
    log_files = find_logs_by_hostname(args.hostname)
    
    if not log_files:
        print(f"[-] Aucun log trouvé pour le hostname: {args.hostname}")
        sys.exit(1)
    
    # Trier les fichiers par date (plus récent en premier)
    log_files.sort(reverse=True)
    
    # Limiter aux fichiers à traiter
    if args.latest:
        log_files = log_files[:1]
    
    print(f"[+] {len(log_files)} fichier(s) de log trouvé(s) pour {args.hostname}\n")
    
    # Analyser et afficher les résultats
    results = []
    for log_file in log_files:
        result = parse_log_file(log_file, private_key)
        if result:
            results.append(result)
    
    # Afficher les résultats
    for i, result in enumerate(results):
        print(f"Log #{i+1}: {result['filename']}")
        print(f"  Hostname: {result['hostname']}")
        print(f"  Timestamp: {result['timestamp']}")
        print(f"  Clé AES chiffrée: {result['encrypted_key']}")
        print(f"  Clé AES déchiffrée: {result['decrypted_key']}")
        print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())