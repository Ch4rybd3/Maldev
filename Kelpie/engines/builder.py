import yaml

def yaml_to_python_script(yaml_path, output_path):
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Les valeurs à remplacer
    replacements = {
        "{{c2_url}}": "http://10.0.0.10/api",
        "{{folder_path}}": "C:/temp",
        "{{rsa_key_b64}}": "thisisasuperrsakeyinbase64trololo"
    }

    with open(output_path, 'w', encoding='utf-8') as f_out:
        for key, block in data.items():
            # Remplacement dans le bloc
            for placeholder, real_value in replacements.items():
                block = block.replace(placeholder, real_value)

            f_out.write(f"# --- {key} ---\n")
            f_out.write(block)
            f_out.write("\n\n")

if __name__ == "__main__":
    yaml_path = "Kelpie/templates/wannaswim.yml"
    output_path = "Kelpie/malwares/source_code/wannaswim.py"
    yaml_to_python_script(yaml_path, output_path)
    print(f"Script Python généré dans {output_path}")
