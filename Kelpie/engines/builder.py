import yaml
import subprocess
import os
import sys
import shutil

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

    # Appeler pyinstaller pour générer l'exécutable
    build_executable(output_path)


def build_executable(script_path):
    dist_path = os.path.abspath("Kelpie/malwares/dist")
    temp_build_path = os.path.abspath("temp_build")
    os.makedirs(dist_path, exist_ok=True)

    # Chemin vers l’exécutable pyinstaller dans le venv (Windows)
    pyinstaller_exe = os.path.abspath(r"venv\Scripts\pyinstaller.exe")
    if not os.path.exists(pyinstaller_exe):
        print(f"[!] Erreur : impossible de trouver {pyinstaller_exe}")
        return

    cmd = [
        pyinstaller_exe,
        "--onefile",
        "--distpath", dist_path,
        "--workpath", temp_build_path,
        "--specpath", temp_build_path,
        "--noconfirm",
        "--clean",
        script_path
    ]

    print(f"[+] Compilation avec : {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"[+] Executable généré dans : {dist_path}")
    except subprocess.CalledProcessError as e:
        print(f"[!] Erreur PyInstaller : {e}")
        return

    # Nettoyage
    if os.path.exists(temp_build_path):
        shutil.rmtree(temp_build_path)
        print(f"[+] Temporaire supprimé : {temp_build_path}")

    pycache = os.path.join(os.path.dirname(script_path), "__pycache__")
    if os.path.exists(pycache):
        shutil.rmtree(pycache)
        print(f"[+] __pycache__ supprimé : {pycache}")


if __name__ == "__main__":
    print("Ce module est prévu pour être importé depuis kelpie.py")
