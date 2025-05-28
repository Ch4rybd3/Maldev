import os
import yaml
import questionary

CONFIG_DIR = "Kelpie/config"

# Charger tous les fichiers YAML
def load_all_configs():
    configs = []
    for file in os.listdir(CONFIG_DIR):
        if file.endswith(".yml"):
            path = os.path.join(CONFIG_DIR, file)
            with open(path, "r") as f:
                data = yaml.safe_load(f)
                data["__filename__"] = file  # garder le nom du fichier
                configs.append(data)
    return configs

# Organiser par type
def get_malware_types(configs):
    return sorted(set(conf['malware_type'] for conf in configs))

# === Main ===
all_configs = load_all_configs()

# Étape 1 - Choix du type de malware
malware_type = questionary.select(
    "Select the malware type",
    choices=get_malware_types(all_configs)
).ask()

# Étape 2 - Filtres les payloads disponibles
filtered = [c for c in all_configs if c['malware_type'] == malware_type]

# Étape 3 - Choix du payload
payload = questionary.select(
    "Select the base payload",
    choices=[f"{conf['name']} ({conf['lang']})" for conf in filtered]
).ask()

# Retrouver la config associée
selected_payload = next(conf for conf in filtered if conf['name'] in payload)

# Étape 4 - Affiche la description
print(f"\nDescription:\n{selected_payload['description']}")

# Étape 5 - C2
c2_url = questionary.text(
    "Enter C2 URL",
    default=selected_payload.get("c2_url", "https://example.com")
).ask()

# Étape 6 - Features disponibles
features = questionary.checkbox(
    "Select features",
    choices=selected_payload.get("available_features", [])
).ask()

print("\nRésumé:")
print(f"- Payload     : {selected_payload['name']}")
print(f"- Langage     : {selected_payload['lang']}")
print(f"- C2          : {c2_url}")
print(f"- Features    : {features}")
