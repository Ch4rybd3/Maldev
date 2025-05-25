from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
import logging
import yaml

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Charger le fichier YAML au lancement
with open("auth_key.yml", "r", encoding="utf-8") as f:
    auth_data = yaml.safe_load(f)

RESULTS_BASE_DIR = "results"
os.makedirs(RESULTS_BASE_DIR, exist_ok=True)

def get_malware_from_auth_key(auth_key):
    malware_dict = auth_data.get("malware", {})
    for malware_name, key in malware_dict.items():
        if key == auth_key:
            return malware_name
    return "unknow"

@app.route("/", methods=["POST"])
def handle_request():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "No JSON received"}), 400

    auth_key = data.get("auth_key")
    if not auth_key:
        return jsonify({"status": "error", "message": "Missing auth_key"}), 400

    malware_name = get_malware_from_auth_key(auth_key)
    if malware_name == "unknown":
        logging.warning(f"Clé inconnue reçue : {auth_key}. Enregistrement dans 'unknown'.")

    hostname = data.get("hostname", "unknown_host")
    timestamp_str = data.get("timestamp")
    if timestamp_str:
        # Essaie de parser le timestamp, sinon fallback sur maintenant
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except ValueError:
            timestamp = datetime.utcnow()
    else:
        timestamp = datetime.utcnow()

    # Création dossier spécifique au malware
    malware_dir = os.path.join(RESULTS_BASE_DIR, malware_name)
    os.makedirs(malware_dir, exist_ok=True)

    # Nom du fichier hostname_timestamp.json
    filename = f"{hostname}_{timestamp.strftime('%Y%m%dT%H%M%S%f')}.json"
    filepath = os.path.join(malware_dir, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Requête enregistrée dans {filepath}")
    except Exception as e:
        logging.error(f"Erreur écriture fichier: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "200"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
