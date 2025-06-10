import yaml
import os
from jinja2 import Environment, FileSystemLoader

class KelpieCLI:
    def __init__(self):
        self.payloads = self.load_payloads()
        self.selected_payload = None
        self.config = {}
        print(f"[i] {len(self.payloads)} payload(s) chargés depuis le dossier config.")

    def run(self):
        while True:
            cmd = input("kelpie > ").strip()
            if cmd in ("exit", "quit"):
                break
            self.handle_command(cmd)

    def handle_command(self, cmd):
        if cmd == "list":
            self.list_payloads()
        elif cmd.startswith("use "):
            name = cmd.split(" ", 1)[1]
            self.select_payload(name)
        elif cmd == "show options":
            self.show_options()
        elif cmd.startswith("set"):
            # Extraire la partie après 'set'
            args = cmd[3:].strip()
            self.set_option(args)
        elif cmd == "generate":
            self.generate_payload()
        else:
            print("Commande inconnue.")

    def list_payloads(self):
        for payload in self.payloads:
            print(f"- {payload['name']} ({payload['malware_type']})")

    def select_payload(self, name):
        for p in self.payloads:
            if p["name"].lower() == name.lower():
                self.selected_payload = p
                self.config = {opt["name"]: opt.get("default", "") for opt in p["features"]}
                print(f"Payload '{name}' sélectionné.")
                return
        print("Payload non trouvé.")

    def show_options(self):
        if not self.selected_payload:
            print("Aucun payload sélectionné.")
            return
        for opt in self.selected_payload["features"]:
            value = self.config.get(opt["name"], "")
            print(f"{opt['name']} ({opt['type']}): {value}")

    def set_option(self, args=None):
        if not self.selected_payload:
            print("Aucun payload sélectionné.")
            return
        
        if args:
            parts = args.split(" ", 1)
            if len(parts) != 2:
                print("Usage : set <option> <valeur>")
                return
            opt, val = parts
            if opt not in self.config:
                print("Option inconnue.")
                return
            self.config[opt] = val
            print(f"{opt} mis à jour.")
        else:
            # mode interactif
            opt = input("Nom de l'option à modifier: ").strip()
            if opt not in self.config:
                print("Option inconnue.")
                return
            val = input(f"Nouvelle valeur pour {opt}: ").strip()
            self.config[opt] = val
            print(f"{opt} mis à jour.")

    def generate_payload(self):
        if not self.selected_payload:
            print("Aucun payload sélectionné.")
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(base_dir, "templates")
        output_dir = os.path.join(base_dir, "malwares", "source_code")
        os.makedirs(output_dir, exist_ok=True)

        payload_name = self.selected_payload["name"]
        lang = self.selected_payload.get("lang", "py")
        template_filename = f"{payload_name}.{lang}.j2"

        env = Environment(loader=FileSystemLoader(os.path.join(templates_dir, "base")))

        if not os.path.exists(os.path.join(templates_dir, "base", template_filename)):
            print(f"Template non trouvé : {template_filename}")
            return

        template = env.get_template(template_filename)
        rendered_code = template.render(**self.config)

        output_path = os.path.join(output_dir, f"{payload_name}.{lang}")
        with open(output_path, "w") as f:
            f.write(rendered_code)

        print(f"Payload généré : {output_path}")

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
