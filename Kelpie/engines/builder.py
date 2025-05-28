import yaml

def yaml_to_python_script(yaml_path, output_path):
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Les blocs dans l'ordre d'apparition dans le YAML (car dict Python >=3.7 garde l'ordre)
    with open(output_path, 'w', encoding='utf-8') as f_out:
        for key, block in data.items():
            f_out.write(f"# --- {key} ---\n")
            f_out.write(block)
            f_out.write("\n\n")

if __name__ == "__main__":
    yaml_path = "Kelpie/templates/wannaswim.yml"     # ton fichier yaml
    output_path = "Kelpie/malwares/source_code/wannaswim.py"  # script python généré
    yaml_to_python_script(yaml_path, output_path)
    print(f"Script Python généré dans {output_path}")
