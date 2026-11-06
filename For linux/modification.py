import os
import subprocess
import pandas as pd


def run_openssl(cmd):
  # Remplace automatiquement 'openssl' par le chemin absolu sécurisé
  full_cmd = cmd.replace("openssl", f'"{OPENSSL_PATH}"', 1)
  res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
  return res.returncode, res.stdout.strip(), res.stderr.strip()


#Question 2 : Simulation des altérations et constats de rejets
print("------------------------------------------------------------------")
print("QUESTION 2 : Tests de résistance aux altérations et rejets")
print("------------------------------------------------------------------")

# --- Test 2.1 : Modification d'un octet du fichier original ---
with open("document.bin", "rb") as f:
    data = bytearray(f.read())
data[0] ^= 0xFF  # Inversion des bits du premier octet
with open("file_tampered.bin", "wb") as f:
    f.write(data)

code_t1, _, err_t1 = run_openssl(
    "openssl pkeyutl -verify -in file_tampered.bin -sigfile signed_document_65.sig -pubin -inkey pub_65.pem"
)
status_t1 = "REJETÉ (Succès du test)" if code_t1 != 0 else "ACCEPTÉ (Erreur)"
print(f"1. Fichier binaire altéré d'un octet  : {status_t1}")

# --- Test 2.2 : Vérification avec une autre clé publique ---
run_openssl("openssl genpkey -algorithm ML-DSA-65 -out key_other.pem")
run_openssl("openssl pkey -in key_other.pem -pubout -out pub_other.pem")

code_t2, _, err_t2 = run_openssl(
    "openssl pkeyutl -verify -in document.bin -sigfile signed_document_65.sig -pubin -inkey pub_other.pem"
)
status_t2 = "REJETÉ (Succès du test)" if code_t2 != 0 else "ACCEPTÉ (Erreur)"
print(f"2. Clé publique différente utilisée  : {status_t2}")

# --- Test 2.3 : Vérification avec une signature tronquée ---
with open("signed_document_65.sig", "rb") as f:
    sig_raw = f.read()
# Troncature : conservation des 3000 premiers octets sur 3309
with open("sig_truncated.sig", "wb") as f:
    f.write(sig_raw[:3000])

code_t3, _, err_t3 = run_openssl(
    "openssl pkeyutl -verify -in document.bin -sigfile sig_truncated.sig -pubin -inkey pub_65.pem"
)
status_t3 = "REJETÉ (Succès du test)" if code_t3 != 0 else "ACCEPTÉ (Erreur)"
print(f"3. Signature tronquée à 3000 octets : {status_t3}")
print()


