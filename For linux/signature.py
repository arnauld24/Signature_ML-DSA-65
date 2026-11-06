import os
import subprocess
import pandas as pd

# Indiquez le chemin exact de votre exécutable OpenSSL 3.5 sous Windows
OPENSSL_PATH = r"C:\Program Files\FireDaemon OpenSSL 3.5\bin\openssl.exe"


def run_openssl(cmd):
  # Remplace automatiquement 'openssl' par le chemin absolu sécurisé
  full_cmd = cmd.replace("openssl", f'"{OPENSSL_PATH}"', 1)
  res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
  return res.returncode, res.stdout.strip(), res.stderr.strip()


#Question 1 : Signer un fichier binaire et relever la taille brute

print("------------------------------------------------------------------")
print("QUESTION 1 : Signature binaire, vérification et mesure de taille")
print("------------------------------------------------------------------")

# # 1. Génération de la paire de clés ML-DSA-65
# code, out, err = run_openssl(
#     "openssl genpkey -algorithm ML-DSA-65 -out key_65.pem"
# )
# code_pub, out_pub, err_pub = run_openssl(
#     "openssl pkey -in key_65.pem -pubout -out pub_65.pem"
# )

# # 2. Signature du fichier binaire
# code_sig, out_sig, err_sig = run_openssl(
#     "openssl pkeyutl -sign -in document.bin -inkey key_65.pem -out sig_65.sig"
# )

# # 3. Mesure de la taille brute
# sig_size_q1 = os.path.getsize("sig_65.sig")
# print(f"-> Taille brute du fichier de signature (sig_65.sig) : {sig_size_q1} octets")

# 4. Vérification nominale avec la clé publique
code_ver, out_ver, err_ver = run_openssl(
    "openssl pkeyutl -verify -in document.bin -sigfile sig_65.sig -pubin -inkey pub_65.pem"
)

if code_ver == 0:
    print("-> Statut de vérification initiale : VALIDE (Signature vérifiée)")
else:
    print(f"-> Statut de vérification initiale : ÉCHEC ({err_ver})")
print()
