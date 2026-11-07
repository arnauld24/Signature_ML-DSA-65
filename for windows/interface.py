import os
import subprocess
import sys
import threading
import time

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
    from tkinter.scrolledtext import ScrolledText
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Tkinter est absent. Installez le paquet système pour l’interface graphique :\n"
        "  sudo apt-get install python3-tk\n"
        "puis relancez : python3 gui_launcher.py"
    ) from exc


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXECUTABLE = sys.executable

SCRIPT_DEFINITIONS = [
    ("Exercice principal", "exercise_28.py"),
    ("Comparaison ML-DSA", "comparaison.py"),
    ("Évaluation", "evaluation.py"),
    ("Modification / rejets", "modification.py"),
    ("Vérification de signature", "signature.py"),
    ("Génération fichier binaire", "binary_file.py"),
]


def make_button(parent, text, command, bg, fg="#ffffff", width=16):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        font=("Arial", 10, "bold"),
        height=2,
        padx=10,
        relief="flat",
        width=width,
    )


class ScriptLauncherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Signature ML-DSA - Lanceur GUI")
        self.geometry("1040x720")
        self.minsize(940, 620)
        self.configure(bg="#edf2f7")

        self.process = None
        self.running = False
        self.document_path = tk.StringVar(value=os.path.join(PROJECT_DIR, "document.bin"))
        self.private_key_path = tk.StringVar(value=os.path.join(PROJECT_DIR, "key_65.pem"))
        self.public_key_path = tk.StringVar(value=os.path.join(PROJECT_DIR, "pub_65.pem"))
        self.signature_path = tk.StringVar(value=os.path.join(PROJECT_DIR, "signed_document_65.sig"))
        self.status_label = None

        self._build_ui()
        self.check_openssl()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = tk.Frame(self, bg="#1f2937", padx=20, pady=18)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title = tk.Label(
            header,
            text="Projet SIGNATURE_ML-DSA-65-MAIN",
            fg="white",
            bg="#1f2937",
            font=("Arial", 18, "bold"),
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = tk.Label(
            header,
            text="Lanceur graphique pour signer, vérifier et tester les scripts OpenSSL ML-DSA",
            fg="#d1d5db",
            bg="#1f2937",
            font=("Arial", 10),
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(6, 0))

        status_bg = tk.Frame(header, bg="#1f2937")
        status_bg.grid(row=0, column=1, sticky="e", padx=(20, 0))
        self.status_label = tk.Label(
            status_bg,
            text="Vérification OpenSSL...",
            bg="#1d4ed8",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=12,
            pady=6,
            relief="flat",
        )
        self.status_label.pack(anchor="e")

        main = tk.Frame(self, bg="#edf2f7", padx=18, pady=12)
        main.grid(row=1, column=0, sticky="nsew")
        main.grid_columnconfigure(0, weight=2)
        main.grid_columnconfigure(1, weight=3)
        main.grid_rowconfigure(0, weight=1)

        left = tk.LabelFrame(main, text="Scripts du projet", padx=12, pady=12, bg="#ffffff", font=("Arial", 11, "bold"))
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_columnconfigure(0, weight=1)

        self.buttons = []
        for index, (label, filename) in enumerate(SCRIPT_DEFINITIONS):
            btn = tk.Button(
                left,
                text=f"{label}\n{filename}",
                command=lambda f=filename: self.run_script(f),
                bg="#ecfdf5",
                fg="#14532d",
                font=("Arial", 10, "bold"),
                anchor="w",
                justify="left",
                padx=14,
                pady=11,
                relief="flat",
                borderwidth=1,
                width=28,
                height=2,
                activebackground="#d1fae5",
                activeforeground="#14532d",
                cursor="hand2",
                highlightthickness=0,
            )
            btn.grid(row=index, column=0, sticky="ew", pady=6)
            self.buttons.append(btn)

        right = tk.Frame(main, bg="#edf2f7")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        ops = tk.LabelFrame(right, text="Opérations rapides", padx=12, pady=12, bg="#ffffff", font=("Arial", 11, "bold"))
        ops.grid(row=0, column=0, sticky="ew")
        ops.grid_columnconfigure(1, weight=1)

        self._build_file_field(ops, 0, "Fichier à signer", self.document_path, "Choisir un fichier")
        self._build_file_field(ops, 1, "Clé privée", self.private_key_path, "Choisir la clé privée")
        self._build_file_field(ops, 2, "Signature de sortie", self.signature_path, "Choisir le fichier de signature")
        self._build_file_field(ops, 3, "Clé publique", self.public_key_path, "Choisir la clé publique")

        action_row = tk.Frame(ops, bg="#ffffff")
        action_row.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        action_row.grid_columnconfigure(0, weight=1)
        action_row.grid_columnconfigure(1, weight=1)
        action_row.grid_columnconfigure(2, weight=1)

        self.generate_binary_btn = make_button(action_row, "Générer fichier binaire", self.generate_binary_file, "#f97316", width=22)
        self.generate_binary_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.generate_keys_btn = make_button(action_row, "Générer paire de clés", self.generate_key_pair, "#f59e0b", width=22)
        self.generate_keys_btn.grid(row=0, column=1, sticky="ew", padx=8)

        self.sign_btn = make_button(action_row, "Signer le fichier", self.sign_document, "#2563eb", width=18)
        self.sign_btn.grid(row=0, column=2, sticky="ew", padx=8)

        self.verify_btn = make_button(action_row, "Vérifier la signature", self.verify_signature, "#10b981", width=20)
        self.verify_btn.grid(row=0, column=3, sticky="ew")

        action_bar = tk.Frame(right, bg="#edf2f7", pady=12)
        action_bar.grid(row=1, column=0, sticky="ew")
        action_bar.grid_columnconfigure(0, weight=1)
        action_bar.grid_columnconfigure(1, weight=1)
        action_bar.grid_columnconfigure(2, weight=1)

        self.run_all_btn = make_button(action_bar, "Lancer tout", self.run_all_scripts, "#7c3aed", width=16)
        self.run_all_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.clear_btn = make_button(action_bar, "Nettoyer", self.clear_output, "#e5e7eb", fg="#111827", width=12)
        self.clear_btn.grid(row=0, column=1, sticky="ew", padx=8)

        output_frame = tk.LabelFrame(right, text="Sortie des commandes", padx=10, pady=10, bg="#ffffff", font=("Arial", 11, "bold"))
        output_frame.grid(row=2, column=0, sticky="nsew", pady=(8, 0))
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(0, weight=1)

        self.output = ScrolledText(
            output_frame,
            wrap=tk.WORD,
            height=18,
            font=("Consolas", 10),
            bg="#0f172a",
            fg="#e2e8f0",
            padx=8,
            pady=8,
        )
        self.output.grid(row=0, column=0, sticky="nsew")
        self.output.insert(
            tk.END,
            "Bienvenue dans le lanceur GUI ML-DSA.\n"
            "Vous pouvez lancer un script, signer un fichier ou vérifier une signature.\n\n"
            "Prérequis : OpenSSL installé et disponible dans le PATH.\n",
        )
        self.output.configure(state="disabled")

    def _build_file_field(self, parent, row, label_text, variable, button_text):
        label = tk.Label(parent, text=label_text, bg="#ffffff", font=("Arial", 10, "bold"))
        label.grid(row=row, column=0, sticky="w", pady=5)

        entry = tk.Entry(parent, textvariable=variable, width=50, font=("Arial", 10))
        entry.grid(row=row, column=1, sticky="ew", padx=(8, 8), pady=5)

        btn = tk.Button(parent, text=button_text, command=lambda: self.browse_file(variable, label_text), bg="#dbeafe", fg="#1e3a8a", font=("Arial", 9, "bold"))
        btn.grid(row=row, column=2, sticky="e", pady=5)

    def browse_file(self, variable, field_name):
        path = filedialog.askopenfilename(
            initialdir=PROJECT_DIR,
            title=f"Choisir {field_name}",
        )
        if path:
            variable.set(path)

    def log(self, text):
        self.output.configure(state="normal")
        self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.configure(state="disabled")

    def clear_output(self):
        self.output.configure(state="normal")
        self.output.delete(1.0, tk.END)
        self.output.configure(state="disabled")

    def check_openssl(self):
        try:
            result = subprocess.run(["openssl", "version"], capture_output=True, text=True, cwd=PROJECT_DIR)
            if result.returncode == 0:
                self.status_label.config(text="OpenSSL OK", bg="#15803d")
                self.log("[INFO] OpenSSL détecté et prêt à l’emploi.\n")
            else:
                self.status_label.config(text="OpenSSL absent", bg="#b91c1c")
                self.log("[ATTENTION] OpenSSL n’est pas disponible dans le PATH.\n")
        except FileNotFoundError:
            self.status_label.config(text="OpenSSL absent", bg="#b91c1c")
            self.log("[ATTENTION] Commande OpenSSL introuvable. Vérifiez votre installation.\n")

    def _set_running_state(self, is_running):
        self.running = is_running
        self.run_all_btn.config(state="normal" if not is_running else "disabled")
        for btn in self.buttons:
            btn.config(state="normal" if not is_running else "disabled")
        self.generate_binary_btn.config(state="normal" if not is_running else "disabled")
        self.generate_keys_btn.config(state="normal" if not is_running else "disabled")
        self.sign_btn.config(state="normal" if not is_running else "disabled")
        self.verify_btn.config(state="normal" if not is_running else "disabled")

    def generate_binary_file(self):
        file_path = self.document_path.get().strip()
        if not file_path:
            messagebox.showerror("Chemin manquant", "Indiquez le chemin du fichier binaire.")
            return

        try:
            with open(file_path, "wb") as f:
                f.write(os.urandom(1024))
            self.log(f"\n[INFO] Fichier binaire créé : {file_path}\n")
            messagebox.showinfo("Fichier généré", f"Le fichier binaire a été créé :\n{file_path}")
        except Exception as exc:
            self.log(f"\n[ERREUR] {exc}\n")
            messagebox.showerror("Erreur", str(exc))

    def run_command(self, cmd, label):
        if self.running:
            messagebox.showwarning("Exécution en cours", "Une commande est déjà en cours d’exécution.")
            return

        self.log(f"\n=== {label} ===\n")
        self.log(f"Commande : {' '.join(cmd)}\n")
        start_time = subprocess.run(["python3", "-c", "import time; print(time.time())"], capture_output=True, text=True).stdout.strip()
        start_ts = float(start_time) if start_time else 0.0
        self._set_running_state(True)

        def target():
            try:
                self.process = subprocess.Popen(
                    cmd,
                    cwd=PROJECT_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                self.after(0, lambda: self.log(f"[INFO] Début de l'opération : {label}\n"))
                for line in iter(self.process.stdout.readline, ""):
                    self.after(0, lambda msg=line: self.log(msg))
                return_code = self.process.wait()
                elapsed = time.time() - start_ts
                self.after(0, lambda: self.log(f"\n[INFO] {label} terminé avec le code {return_code} en {elapsed:.2f} secondes.\n"))
                self.after(0, lambda: self._show_result(label, return_code))
            except Exception as exc:
                self.after(0, lambda: self.log(f"\n[ERREUR] {exc}\n"))
            finally:
                self.after(0, lambda: self._set_running_state(False))

        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    def _show_result(self, label, code):
        if code == 0:
            messagebox.showinfo(label, "Opération réussie.")
        else:
            messagebox.showerror(label, f"L’opération a échoué avec le code {code}.")

    def generate_key_pair(self):
        private_key = self.private_key_path.get().strip()
        public_key = self.public_key_path.get().strip()

        if not private_key or not public_key:
            messagebox.showerror("Chemins manquants", "Indiquez les chemins de la clé privée et publique.")
            return

        cmd = [
            "openssl",
            "genpkey",
            "-algorithm",
            "ML-DSA-65",
            "-out",
            private_key,
        ]
        self.run_command(cmd, "GÉNÉRATION DE LA CLÉ PRIVÉE")

        pub_cmd = [
            "openssl",
            "pkey",
            "-in",
            private_key,
            "-pubout",
            "-out",
            public_key,
        ]

        def do_public_key_generation():
            try:
                self.process = subprocess.Popen(
                    pub_cmd,
                    cwd=PROJECT_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                for line in iter(self.process.stdout.readline, ""):
                    self.after(0, lambda msg=line: self.log(msg))
                return_code = self.process.wait()
                self.after(0, lambda: self.log(f"\n[INFO] GÉNÉRATION DE LA CLÉ PUBLIQUE terminée avec le code {return_code}.\n"))
                self.after(0, lambda: self._show_result("GÉNÉRATION DE LA PAIRE DE CLÉS", return_code))
            except Exception as exc:
                self.after(0, lambda: self.log(f"\n[ERREUR] {exc}\n"))
            finally:
                self.after(0, lambda: self._set_running_state(False))

        def run_generation():
            self.log(f"\n=== GÉNÉRATION DE LA PAIRE DE CLÉS ===\n")
            self.log(f"Commande privée : {' '.join(cmd)}\n")
            self.log(f"Commande publique : {' '.join(pub_cmd)}\n")
            self._set_running_state(True)

            def inner():
                try:
                    start_time = time.time()
                    self.process = subprocess.Popen(
                        cmd,
                        cwd=PROJECT_DIR,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                    )
                    for line in iter(self.process.stdout.readline, ""):
                        self.after(0, lambda msg=line: self.log(msg))
                    return_code = self.process.wait()
                    elapsed = time.time() - start_time
                    self.after(0, lambda: self.log(f"\n[INFO] Clé privée créée en {elapsed:.2f} secondes.\n"))
                    if return_code == 0:
                        self.after(0, do_public_key_generation)
                    else:
                        self.after(0, lambda: self._show_result("GÉNÉRATION DE LA PAIRE DE CLÉS", return_code))
                        self.after(0, lambda: self._set_running_state(False))
                except Exception as exc:
                    self.after(0, lambda: self.log(f"\n[ERREUR] {exc}\n"))
                    self.after(0, lambda: self._set_running_state(False))

            threading.Thread(target=inner, daemon=True).start()

        run_generation()

    def sign_document(self):
        document = self.document_path.get().strip()
        key = self.private_key_path.get().strip()
        output = self.signature_path.get().strip()

        if not os.path.exists(document):
            messagebox.showerror("Fichier manquant", "Le fichier à signer est introuvable.")
            return
        if not os.path.exists(key):
            messagebox.showerror("Clé manquante", "La clé privée est introuvable.")
            return

        cmd = ["openssl", "pkeyutl", "-sign", "-in", document, "-inkey", key, "-out", output]
        self.run_command(cmd, "SIGNATURE DU FICHIER")

    def verify_signature(self):
        document = self.document_path.get().strip()
        signature = self.signature_path.get().strip()
        public_key = self.public_key_path.get().strip()

        if not os.path.exists(document):
            messagebox.showerror("Fichier manquant", "Le document est introuvable.")
            return
        if not os.path.exists(signature):
            messagebox.showerror("Signature manquante", "Le fichier de signature est introuvable.")
            return
        if not os.path.exists(public_key):
            messagebox.showerror("Clé manquante", "La clé publique est introuvable.")
            return

        cmd = ["openssl", "pkeyutl", "-verify", "-in", document, "-sigfile", signature, "-pubin", "-inkey", public_key]
        self.run_command(cmd, "VÉRIFICATION DE LA SIGNATURE")

    def run_script(self, script_name):
        script_path = os.path.join(PROJECT_DIR, script_name)
        if not os.path.exists(script_path):
            messagebox.showerror("Script introuvable", f"Le fichier {script_name} est absent.")
            return

        if self.running:
            messagebox.showwarning("Exécution en cours", "Une commande est déjà en cours d’exécution.")
            return

        self.log(f"\n=== LANCEMENT : {script_name} ===\n")
        self._set_running_state(True)

        def target():
            start_time = time.time()
            try:
                self.process = subprocess.Popen(
                    [PYTHON_EXECUTABLE, script_path],
                    cwd=PROJECT_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                for line in iter(self.process.stdout.readline, ""):
                    self.after(0, lambda msg=line: self.log(msg))
                return_code = self.process.wait()
                elapsed = time.time() - start_time
                self.after(0, lambda: self.log(f"\n[INFO] Script terminé avec le code {return_code} en {elapsed:.2f} secondes.\n"))
            except Exception as exc:
                self.after(0, lambda: self.log(f"\n[ERREUR] {exc}\n"))
            finally:
                self.after(0, lambda: self._set_running_state(False))

        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    def run_all_scripts(self):
        if self.running:
            messagebox.showwarning("Exécution en cours", "Veuillez attendre la fin de la commande actuelle.")
            return

        self.clear_output()
        self.log("=== LANCEMENT SEQUENCIEL DE TOUS LES SCRIPTS ===\n")
        for _, script_name in SCRIPT_DEFINITIONS:
            self.log(f"\n--- {script_name} ---\n")
            self.run_script(script_name)
            while self.running:
                self.update_idletasks()
                self.update()


if __name__ == "__main__":
    app = ScriptLauncherApp()
    app.mainloop()
