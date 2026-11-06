import os
import subprocess
import pandas as pd


def run_openssl(cmd):
  # Remplace automatiquement 'openssl' par le chemin absolu sécurisé
  full_cmd = cmd.replace("openssl", f'"{OPENSSL_PATH}"', 1)
  res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
  return res.returncode, res.stdout.strip(), res.stderr.strip()

ctx_origin = "ENSPY_INFO_2026"
ctx_wrong = "ENSPY_AUTRE_CTX"

# 1. Création d'une signature avec le contexte 'ENSPY_INFO_2026'
run_openssl(
    f'openssl pkeyutl -sign -in document.bin -inkey key_65.pem -out sig_ctx.sig -pkeyopt context-string:"{ctx_origin}"'
)

# 2. Vérification avec le contexte exact
code_c1, _, _ = run_openssl(
    f'openssl pkeyutl -verify -in document.bin -sigfile sig_ctx.sig -pubin -inkey pub_65.pem -pkeyopt context-string:"{ctx_origin}"'
)
status_c1 = "VALIDE" if code_c1 == 0 else "INVALIDE"
print(f"1. Vérification avec contexte exact ('{ctx_origin}')   : {status_c1}")

# 3. Vérification avec un contexte mismatch
code_c2, _, err_c2 = run_openssl(
    f'openssl pkeyutl -verify -in document.bin -sigfile sig_ctx.sig -pubin -inkey pub_65.pem -pkeyopt context-string:"{ctx_wrong}"'
)
status_c2 = "REJETÉ (Conforme)" if code_c2 != 0 else "ACCEPTÉ (Erreur)"
print(f"2. Vérification avec contexte erroné ('{ctx_wrong}') : {status_c2}")
print()
