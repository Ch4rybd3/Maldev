import yaml
import os
import platform
from jinja2 import Environment, FileSystemLoader
from tabulate import tabulate  # pip install tabulate

class KelpieCLI:
    def __init__(self):
        self.payloads = self.load_payloads()
        self.selected_payload = None
        self.config = {}
        print(f"[i] {len(self.payloads)} payload(s) chargés depuis le dossier config.")

    def clear_console(self):
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

    def truncate_str(self, s, max_len=30):
        if len(s) > max_len:
            return s[:max_len] + "..."
        return s

    def color_text(self, text, color_code):
        return f"\033[{color_code}m{text}\033[0m"

    def green(self, text):
        return self.color_text(text, "32")

    def blue(self, text):
        return self.color_text(text, "34")

    def print_options_table(self):
        if not self.selected_payload:
            print("[Aucun payload sélectionné]")
            return
        headers = ["Nom", "Type", "Mandatory", "Description", "Valeur"]
        rows = []
        for opt in self.selected_payload["features"]:
            name = opt.get("name", "")
            typ = opt.get("type", "")
            mand = opt.get("mandatory", False)
            desc = opt.get("description", "")
            val = self.config.get(name, "")
            val_trunc = self.truncate_str(str(val), 40)  # Limite à 40 caractères par ex

            # Couleur pour mandatory
            if mand is True:
                mand_colored = self.green("True")
            elif mand is False:
                mand_colored = self.blue("False")
            else:
                mand_colored = str(mand)

            # Couleur pour la valeur modifiée
            # On récupère la valeur par défaut dans la config du payload
            default_val = ""
            for feature in self.selected_payload["features"]:
                if feature.get("name") == name:
                    default_val = feature.get("default", "")
                    break
            if val != default_val:
                val_colored = self.green(val_trunc)
            else:
                val_colored = val_trunc

            rows.append([name, typ, mand_colored, desc, val_colored])
        print(tabulate(rows, headers=headers, tablefmt="grid"))


    def run(self):
        while True:
            self.clear_console()
            # Affiche tableau options en haut
            self.print_options_table()

            # Affiche prompt avec ou sans payload sélectionné
            prompt = "[kelpie]"
            if self.selected_payload:
                prompt += f" - [{self.selected_payload['name']}]"
            prompt += " > "
            
            cmd = input(prompt).strip()
            if cmd in ("exit", "quit"):
                break
            self.handle_command(cmd)

    def handle_command(self, cmd):
        if cmd == "list":
            self.list_payloads()
            input("\nAppuyez sur Entrée pour continuer...")
        elif cmd.startswith("use "):
            name = cmd.split(" ", 1)[1]
            self.select_payload(name)
        elif cmd == "show options":
            self.show_options()
        elif cmd.startswith("set"):
            args = cmd[3:].strip()
            self.set_option(args)
        elif cmd == "generate":
            self.generate_payload()
            input("\nAppuyez sur Entrée pour continuer...")
        else:
            print("Commande inconnue.")
            input("\nAppuyez sur Entrée pour continuer...")

    def list_payloads(self):
        print("Payloads disponibles :")
        for payload in self.payloads:
            print(f"- {payload['name']} ({payload['malware_type']}) ({payload['lang']})")

    def select_payload(self, name):
        for p in self.payloads:
            if p["name"].lower() == name.lower():
                self.selected_payload = p
                self.config = {opt["name"]: opt.get("default", "") for opt in p["features"]}
                print(f"Payload '{name}' sélectionné.")
                return
        print("Payload non trouvé.")
        input("\nAppuyez sur Entrée pour continuer...")

    def show_options(self):
        if not self.selected_payload:
            print("Aucun payload sélectionné.")
            return
        print("Options du payload :")
        for opt in self.selected_payload["features"]:
            value = self.config.get(opt["name"], "")
            print(f"{opt['name']} ({opt['type']}): {value}")

    def set_option(self, args=None):
        if not self.selected_payload:
            print("Aucun payload sélectionné.")
            input("\nAppuyez sur Entrée pour continuer...")
            return
        
        if args:
            parts = args.split(" ", 1)
            if len(parts) != 2:
                print("Usage : set <option> <valeur>")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            opt, val = parts
            if opt not in self.config:
                print("Option inconnue.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            self.config[opt] = val
            print(f"{opt} mis à jour.")
        else:
            opt = input("Nom de l'option à modifier: ").strip()
            if opt not in self.config:
                print("Option inconnue.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            val = input(f"Nouvelle valeur pour {opt}: ").strip()
            self.config[opt] = val
            print(f"{opt} mis à jour.")

    def generate_payload(self):
        if not self.selected_payload:
            print("[ERREUR] Aucun payload sélectionné.")
            return

        print(f"[DEBUG] Payload sélectionné : {self.selected_payload['name']}")

        base_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(base_dir, "templates")
        output_dir = os.path.join(base_dir, "malwares", "source_code")
        os.makedirs(output_dir, exist_ok=True)

        print(f"[DEBUG] Répertoire base : {base_dir}")
        print(f"[DEBUG] Répertoire des templates : {templates_dir}")
        print(f"[DEBUG] Répertoire de sortie : {output_dir}")

        payload_name = self.selected_payload["name"]
        lang = self.selected_payload.get("lang", "py")
        template_filename = f"{payload_name}.j2"
        template_path = os.path.join(templates_dir, "base", template_filename)

        print(f"[DEBUG] Nom du template attendu : {template_filename}")
        print(f"[DEBUG] Chemin complet du template : {template_path}")

        env = Environment(loader=FileSystemLoader(os.path.join(templates_dir, "base")))

        if not os.path.exists(template_path):
            print(f"[ERREUR] Template non trouvé : {template_filename}")
            return

        try:
            print("[INFO] Rendu du template en cours...")
            template = env.get_template(template_filename)
            rendered_code = template.render(**self.config)
        except Exception as e:
            print(f"[ERREUR] Échec du rendu du template : {e}")
            return

        output_path = os.path.join(output_dir, f"{payload_name}.{lang}")
        try:
            with open(output_path, "w") as f:
                f.write(rendered_code)
            print(f"[SUCCÈS] Payload généré : {output_path}")
        except Exception as e:
            print(f"[ERREUR] Écriture du fichier échouée : {e}")


    def load_payloads(self):
        payloads = []
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(base_dir, "config")

        for file in os.listdir(config_dir):
            if file.endswith(".yml") or file.endswith(".yaml"):
                with open(os.path.join(config_dir, file), "r") as f:
                    payloads.append(yaml.safe_load(f))
        return payloads


if __name__ == "__main__":
    cli = KelpieCLI()
    cli.run()
