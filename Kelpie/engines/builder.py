# Kelpie/engines/builder.py

import yaml

def yaml_to_python_script(yaml_path, output_path, replacements):
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    with open(output_path, 'w', encoding='utf-8') as f_out:
        for key, block in data.items():
            for placeholder, real_value in replacements.items():
                block = block.replace(placeholder, real_value)
            f_out.write(f"# --- {key} ---\n")
            f_out.write(block)
            f_out.write("\n\n")

    print(f"[+] Script généré dans : {output_path}")

if __name__ == "__main__":
    print("Ce module est prévu pour être importé depuis kelpie.py")
