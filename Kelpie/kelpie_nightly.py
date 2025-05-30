import os
import sys
import re
import yaml
import questionary
from jinja2 import Template

TEMPLATE_DIR = "Kelpie/templates/payloads"
FUNC_DIR = "Kelpie/templates/functionnality"
DIST_DIR = "Kelpie/malwares/dist"

def extract_metadata_from_template(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'{#---(.*?)---#}', content, re.DOTALL)
    if not match:
        raise ValueError(f"Aucun bloc de métadonnées YAML trouvé dans {path}")
    yaml_block = match.group(1)
    metadata = yaml.safe_load(yaml_block)
    return metadata

def list_payloads():
    return [f for f in os.listdir(TEMPLATE_DIR) if f.endswith(".j2")]

def list_functionnalities():
    return [f for f in os.listdir(FUNC_DIR) if f.endswith(".j2")]

def extract_start_function(template_content):
    match = re.search(r'{%\s*set\s+start\s*=\s*"([^"]+)"\s*%}', template_content)
    return match.group(1) if match else "main"

def extract_imports(code):
    """Extrait toutes les lignes d'import pour éviter les doublons"""
    imports = []
    other_code = []
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            if line not in imports:
                imports.append(line)
        else:
            other_code.append(line)
    return imports, other_code

def main():
    print("\n🚀 Bienvenue dans Kelpie - Générateur multi-payloads personnalisés\n")

    payload_files = list_payloads()
    if not payload_files:
        print("Aucun template trouvé dans le dossier templates.")
        sys.exit(1)

    selected_payloads = questionary.checkbox(
        "📦 Choisissez un ou plusieurs payloads à combiner :",
        choices=payload_files
    ).ask()

    if not selected_payloads:
        print("Aucun payload sélectionné, sortie.")
        sys.exit(0)

    # Liste des fonctionnalités disponibles (ex: killswitch)
    functionnality_files = list_functionnalities()
    selected_functionnalities = questionary.checkbox(
        "⚙️ Choisissez des fonctionnalités à ajouter (optionnel) :",
        choices=functionnality_files
    ).ask() or []

    all_imports = []
    all_code_blocks = []
    start_functions = []
    output_names = []

    # --- Chargement des payloads ---
    for payload_file in selected_payloads:
        path = os.path.join(TEMPLATE_DIR, payload_file)
        metadata = extract_metadata_from_template(path)
        output_names.append(metadata['name'].lower().replace(" ", "_"))

        print(f"\n🔍 Chargement du template: {metadata['name']} ({metadata['malware_type']})")

        with open(path, encoding='utf-8') as f:
            template_content = f.read()

        # Extraction variables Jinja2
        variables = {}
        keys = set(re.findall(r"{{\s*(\w+)\s*}}", template_content))
        for key in keys:
            if key not in variables:
                response = questionary.text(f"[{metadata['name']}] Entrez une valeur pour '{key}':").ask()
                variables[key] = response

        template = Template(template_content)
        rendered_code = template.render(**variables)

        # Extraction imports et reste du code
        imports, code_lines = extract_imports(rendered_code)

        # Ajout imports sans doublons
        for imp in imports:
            if imp not in all_imports:
                all_imports.append(imp)

        # Stockage code (sans imports)
        all_code_blocks.append("\n".join(code_lines))

        # Extraction fonction de démarrage
        start_func = extract_start_function(template_content)
        start_functions.append(start_func)

    # --- Chargement des fonctionnalités ---
    killswitch_enabled = False
    for func_file in selected_functionnalities:
        path = os.path.join(FUNC_DIR, func_file)
        metadata = extract_metadata_from_template(path)

        print(f"\n🔧 Ajout de la fonctionnalité: {metadata.get('name', func_file)}")

        with open(path, encoding='utf-8') as f:
            func_content = f.read()

        template = Template(func_content)
        # Pas de variables pour l’instant dans les fonctionnalités, sinon tu peux les gérer comme pour les payloads
        rendered_func = template.render()

        # Extraction imports + code
        imports, code_lines = extract_imports(rendered_func)

        for imp in imports:
            if imp not in all_imports:
                all_imports.append(imp)

        all_code_blocks.append("\n".join(code_lines))

        # Si la fonctionnalité est killswitch, on active le flag
        if metadata.get('functionnality_type', '').lower() == 'killswitch':
            killswitch_enabled = True

    # Construction du code final
    final_code = "\n".join(all_imports) + "\n\n"
    final_code += "\n\n".join(all_code_blocks)

    # Génération main avec killswitch conditionnel
    main_code = "\n\nif __name__ == '__main__':\n"
    if killswitch_enabled:
        main_code += "    import sys\n"
        main_code += "    if killswitch():\n"
        main_code += "        sys.exit()\n"
        main_code += "    else:\n"
        for func in start_functions:
            main_code += f"        {func}()\n"
    else:
        for func in start_functions:
            main_code += f"    {func}()\n"

    final_code += main_code

    # Nom fichier de sortie concaténant tous les noms
    output_filename = "_".join(output_names) + ".py"
    output_path = os.path.join(DIST_DIR, output_filename)

    os.makedirs(DIST_DIR, exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as f:
        f.write(final_code)

    print(f"\n✅ Payload(s) combiné(s) généré(s) avec succès : {output_path}\n")

if __name__ == "__main__":
    main()
