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

# Poser dynamiquement les questions pour les specific_feature
def ask_specific_features(specific_features):
    user_answers = {}
    for key, meta in specific_features.items():
        label = f"{meta.get('label', key)}\n{meta.get('description', '')}"

        if meta["type"] == "text":
            user_answers[key] = questionary.text(
                label,
                default=str(meta.get("default", ""))
            ).ask()

        elif meta["type"] == "boolean":
            user_answers[key] = questionary.confirm(
                label,
                default=bool(meta.get("default", False))
            ).ask()

        # Ajouter ici d'autres types si nécessaire

    return user_answers

# === Main ===
all_configs = load_all_configs()

# Étape 1 - Choix du type de malware
malware_type = questionary.select(
    "Select the malware type",
    choices=get_malware_types(all_configs)
).ask()

# Étape 2 - Filtres les payloads disponibles
filtered = [c for c in all_configs if c['malware_type'] == malware_type]

# Step 3 - Select a payload and confirm
while True:
    payload = questionary.select(
        "Select the base payload",
        choices=[f"{conf['name']} ({conf['lang']})" for conf in filtered]
    ).ask()

    # Retrouver la config associée
    selected_payload = next(conf for conf in filtered if conf['name'] in payload)

    # Étape 4 - Affiche la description
    print(f"\nDescription:\n{selected_payload['description']}")

    # Étape 5 - Confirmation
    confirm = questionary.confirm(
        "Do you want to continue with this payload?", default=True
    ).ask()

    if confirm:
        break  # On sort de la boucle si l'utilisateur confirme
    if not confirm:
        print("\nReturning to payload selection...\n")

# Étape 6 - Saisie des champs spécifiques (remplace c2_url statique)
specific_values = ask_specific_features(selected_payload.get("specific_feature", {}))

# Étape 6 - Features disponibles
features = questionary.checkbox(
    "Select features",
    choices=selected_payload.get("available_features", [])
).ask()

# Résumé
print("\nRésumé:")
print(f"- Payload     : {selected_payload['name']}")
print(f"- Langage     : {selected_payload['lang']}")
print(f"- Features    : {features}")
print("- Specific Configuration:")
for key, val in specific_values.items():
    print(f"  - {key}: {val}")