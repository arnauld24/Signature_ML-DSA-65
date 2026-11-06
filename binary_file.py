import os
import subprocess
import pandas as pd


def run_openssl(cmd):
    """Exécute une commande OpenSSL et retourne le code de retour, stdout et stderr."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


print("==================================================================")
print("  EXERCICE 28 : ML-DSA - SIGNER, VÉRIFIER ET CONSTATER LES REJETS")
print("==================================================================\n")

# Nettoyage préalable des fichiers de travail
files_to_clean = [
    "file.bin",
    "file_tampered.bin",
    "key_65.pem",
    "pub_65.pem",
    "key_other.pem",
    "pub_other.pem",
    "sig_65.sig",
    "sig_truncated.sig",
    "sig_ctx.sig",
]
for f in files_to_clean:
    if os.path.exists(f):
        os.remove(f)

# Création d'un fichier binaire aléatoire de 1 Ko (1024 octets)
with open("document.bin", "wb") as f:
    f.write(os.urandom(1024))

# 3. Mesure de la taille brute
sig_size_q1 = os.path.getsize("document.bin")
print(f"-> Taille brute du fichier de signature (sig_65.sig) : {sig_size_q1} octets")

print("[+] Fichier binaire 'document.bin' (1024 octets) créé avec succès.\n")
