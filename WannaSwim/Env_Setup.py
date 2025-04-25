# This is a script that will setup an environnement with random values for the WannaSwim malware.
# It should create a folder under the user Documents which will be named CTF-FSA-002_Documents.
# It will contains folders, ... that will imitate an user directory with pictures, documents, ...
# Author : ch4rybd3@protonmail.com

from pathlib import Path
import random
import csv

import shutil
import os
from pathlib import Path

def setup_and_populate_fake_env():
    # Répertoires sources
    source_dir = Path(__file__).parent / "fake_env_template"  # source directory contenant le modèle de l'environnement fictif
    documents_path = Path.home() / "Documents"  # Chemin des documents de l'utilisateur
    fake_root = documents_path / "CTF-FSA-002_Documents"  # Création du répertoire principal de l'environnement fictif
    folders = ["Documents", "Downloads", "Images", "Videos", "Desktop", "Music"]  # Dossiers classiques dans un répertoire utilisateur

    try:
        # Créer l'environnement utilisateur fictif
        fake_root.mkdir(parents=True, exist_ok=True)
        for folder in folders:
            (fake_root / folder).mkdir(exist_ok=True)  # Créer chaque dossier dans l'environnement fictif
        print(f"L'environnement fictif a été créé ici : {fake_root}")

        # Copier les fichiers dans les dossiers créés
        for folder in folders:
            source_folder = source_dir / folder
            target_folder = fake_root / folder
            if not target_folder.exists():
                target_folder.mkdir(parents=True, exist_ok=True)  # Créer le dossier cible s'il n'existe pas

            if source_folder.exists():  # Copier les fichiers
                for file_name in os.listdir(source_folder):
                    source_file = source_folder / file_name
                    target_file = target_folder / file_name
                    try:
                        shutil.copy(source_file, target_file)
                        print(f"Le fichier a été copié : {file_name} vers {target_folder}")
                    except Exception as e:
                        print(f"Erreur lors de la copie de {file_name} : {e}")
    except Exception as e:
        print(f"Erreur lors de la création de l'environnement fictif : {e}")

# Appeler la fonction pour créer et remplir l'environnement
setup_and_populate_fake_env()


def generate_password_csv():
    # Exemple de noms et prénoms
    noms = ["dupont", "lefevre", "morel", "bernard", "robert", "lambert"]
    prenoms = ["alice", "julien", "marie", "thomas", "lucas", "emma"]
    # Nom du fichier et chemin de destination
    base_path = Path.home() / "Documents" / "CTF-FSA-002_Documents" / "Documents"
    base_path.mkdir(parents=True, exist_ok=True)
    csv_path = base_path / "production_password.csv"
    # Création du CSV
    with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Identifiant", "Mot de passe"])  # en-têtes
        for _ in range(50):  # 50 identifiants
            nom = random.choice(noms)
            prenom = random.choice(prenoms)
            identifiant = f"{nom}.{prenom}@entreprise.fr"
            password = ''.join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@$", k=12))
            writer.writerow([identifiant, password])
    print(f"Fichier généré : {csv_path}")

# Main
setup_and_populate_fake_env()
generate_password_csv()
