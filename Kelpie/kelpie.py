import os
import sys
import yaml
import re
import questionary
from jinja2 import Template

TEMPLATE_DIR = "Kelpie/templates/payloads"
DIST_DIR = "Kelpie/malwares/dist"

# --- Fonction pour extraire les métadonnées YAML d'un template Jinja2 ---
def extract_metadata_from_template(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.search(r'{#---(.*?)---#}', content, re.DOTALL)
    if not match:
        raise ValueError("Aucun bloc de métadonnées YAML trouvé dans le template.")

    yaml_block = match.group(1)
    metadata = yaml.safe_load(yaml_block)
    return metadata

# --- Fonction pour afficher la liste des payloads disponibles ---
def list_payloads():
    payloads = []
    for file in os.listdir(TEMPLATE_DIR):
        if file.endswith(".j2"):
            payloads.append(file)
    return payloads

# --- Fonction principale ---
def main():
    print("\n🚀 Bienvenue dans Kelpie - Générateur de payloads personnalisés\n")

    # Sélection du template
    payload_files = list_payloads()
    if not payload_files:
        print("Aucun template trouvé dans le dossier templates.")
        sys.exit(1)

    payload_choice = questionary.select(
        "📦 Choisissez un payload :",
        choices=payload_files
    ).ask()

    template_path = os.path.join(TEMPLATE_DIR, payload_choice)
    metadata = extract_metadata_from_template(template_path)

    print(f"\n🔍 Chargement du template: {metadata['name']} ({metadata['malware_type']})")

    # Collecte des variables spécifiques (si présentes dans le template)
    variables = {}
    for key in re.findall(r"{{\s*(\w+)\s*}}", open(template_path, encoding='utf-8').read()):
        if key not in variables:
            response = questionary.text(f"Entrez une valeur pour '{key}':").ask()
            variables[key] = response

    # Génération du fichier final
    with open(template_path, encoding='utf-8') as f:
        template_content = f.read()
    template = Template(template_content)
    rendered_code = template.render(**variables)

    output_filename = metadata['name'].lower().replace(" ", "_") + ".py"
    output_path = os.path.join(DIST_DIR, output_filename)

    os.makedirs(DIST_DIR, exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as f:
        f.write(rendered_code)

    print(f"\n✅ Payload généré avec succès : {output_path}\n")


if __name__ == "__main__":
    main()
