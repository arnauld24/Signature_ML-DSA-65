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
with open("file.bin", "wb") as f:
    f.write(os.urandom(1024))

print("[+] Fichier binaire 'file.bin' (1024 octets) créé avec succès.\n")





#Question 1 : Signer un fichier binaire et relever la taille brute

print("------------------------------------------------------------------")
print("QUESTION 1 : Signature binaire, vérification et mesure de taille")
print("------------------------------------------------------------------")

# 1. Génération de la paire de clés ML-DSA-65
code, out, err = run_openssl(
    "openssl genpkey -algorithm ML-DSA-65 -out key_65.pem"
)
code_pub, out_pub, err_pub = run_openssl(
    "openssl pkey -in key_65.pem -pubout -out pub_65.pem"
)

# 2. Signature du fichier binaire
code_sig, out_sig, err_sig = run_openssl(
    "openssl pkeyutl -sign -in file.bin -inkey key_65.pem -out sig_65.sig"
)

# 3. Mesure de la taille brute
sig_size_q1 = os.path.getsize("sig_65.sig")
print(f"-> Taille brute du fichier de signature (sig_65.sig) : {sig_size_q1} octets")

# 4. Vérification nominale avec la clé publique
code_ver, out_ver, err_ver = run_openssl(
    "openssl pkeyutl -verify -in file.bin -sigfile sig_65.sig -pubin -inkey pub_65.pem"
)

if code_ver == 0:
    print("-> Statut de vérification initiale : VALIDE (Signature vérifiée)")
else:
    print(f"-> Statut de vérification initiale : ÉCHEC ({err_ver})")
print()



#Question 2 : Simulation des altérations et constats de rejets
print("------------------------------------------------------------------")
print("QUESTION 2 : Tests de résistance aux altérations et rejets")
print("------------------------------------------------------------------")

# --- Test 2.1 : Modification d'un octet du fichier original ---
with open("file.bin", "rb") as f:
    data = bytearray(f.read())
data[0] ^= 0xFF  # Inversion des bits du premier octet
with open("file_tampered.bin", "wb") as f:
    f.write(data)

code_t1, _, err_t1 = run_openssl(
    "openssl pkeyutl -verify -in file_tampered.bin -sigfile sig_65.sig -pubin -inkey pub_65.pem"
)
status_t1 = "REJETÉ (Succès du test)" if code_t1 != 0 else "ACCPETÉ (Erreur)"
print(f"1. Fichier binaire altéré d'un octet  : {status_t1}")

# --- Test 2.2 : Vérification avec une autre clé publique ---
run_openssl("openssl genpkey -algorithm ML-DSA-65 -out key_other.pem")
run_openssl("openssl pkey -in key_other.pem -pubout -out pub_other.pem")

code_t2, _, err_t2 = run_openssl(
    "openssl pkeyutl -verify -in file.bin -sigfile sig_65.sig -pubin -inkey pub_other.pem"
)
status_t2 = "REJETÉ (Succès du test)" if code_t2 != 0 else "ACCEPTÉ (Erreur)"
print(f"2. Clé publique différente utilisée  : {status_t2}")

# --- Test 2.3 : Vérification avec une signature tronquée ---
with open("sig_65.sig", "rb") as f:
    sig_raw = f.read()
# Troncature : conservation des 3000 premiers octets sur 3309
with open("sig_truncated.sig", "wb") as f:
    f.write(sig_raw[:3000])

code_t3, _, err_t3 = run_openssl(
    "openssl pkeyutl -verify -in file.bin -sigfile sig_truncated.sig -pubin -inkey pub_65.pem"
)
status_t3 = "REJETÉ (Succès du test)" if code_t3 != 0 else "ACCEPTÉ (Erreur)"
print(f"3. Signature tronquée à 3000 octets : {status_t3}")
print()



#Question 3 : Test de la séparation de domaine (context-string)
print("------------------------------------------------------------------")
print("QUESTION 3 : Évaluation du paramètre de contexte (context-string)")
print("------------------------------------------------------------------")

ctx_origin = "ENSPY_INFO_2026"
ctx_wrong = "ENSPY_AUTRE_CTX"

# 1. Création d'une signature avec le contexte 'ENSPY_INFO_2026'
run_openssl(
    f'openssl pkeyutl -sign -in file.bin -inkey key_65.pem -out sig_ctx.sig -pkeyopt context-string:"{ctx_origin}"'
)

# 2. Vérification avec le contexte exact
code_c1, _, _ = run_openssl(
    f'openssl pkeyutl -verify -in file.bin -sigfile sig_ctx.sig -pubin -inkey pub_65.pem -pkeyopt context-string:"{ctx_origin}"'
)
status_c1 = "VALIDE" if code_c1 == 0 else "INVALIDE"
print(f"1. Vérification avec contexte exact ('{ctx_origin}')   : {status_c1}")

# 3. Vérification avec un contexte mismatch
code_c2, _, err_c2 = run_openssl(
    f'openssl pkeyutl -verify -in file.bin -sigfile sig_ctx.sig -pubin -inkey pub_65.pem -pkeyopt context-string:"{ctx_wrong}"'
)
status_c2 = "REJETÉ (Conforme)" if code_c2 != 0 else "ACCEPTÉ (Erreur)"
print(f"2. Vérification avec contexte erroné ('{ctx_wrong}') : {status_c2}")
print()

#Question 4 : Comparaison expérimentale des variantes et analyse réseau
print("------------------------------------------------------------------")
print("QUESTION 4 : Comparaison des profils ML-DSA et impact réseau")
print("------------------------------------------------------------------")

algos = ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]
results = []

for algo in algos:
    kfile = f"key_{algo}.pem"
    pfile = f"pub_{algo}.pem"
    sfile = f"sig_{algo}.sig"

    # Génération clé et signature
    run_openssl(f"openssl genpkey -algorithm {algo} -out {kfile}")
    run_openssl(f"openssl pkey -in {kfile} -pubout -out {pfile}")
    run_openssl(f"openssl pkeyutl -sign -in file.bin -inkey {kfile} -out {sfile}")

    pub_size = os.path.getsize(pfile)
    sig_size = os.path.getsize(sfile)

    results.append(
        {
            "Algorithme": algo,
            "Taille Clé Publique (Octets)": pub_size,
            "Taille Signature (Octets)": sig_size,
        }
    )

    # Nettoyage
    for f in [kfile, pfile, sfile]:
        if os.path.exists(f):
            os.remove(f)

# Affichage du tableau récapitulatif
df_results = pd.DataFrame(results)
print(df_results.to_string(index=False))

print("\n--- ANALYSE DE L'IMPACT SUR LES PROTOCOLES DE TRANSPORT ---")
print(
    "1. Fragmentation IP : Le MTU Ethernet standard étant de 1500 octets (MSS ~1460 octets),\n"
    "   une signature ML-DSA-65 (3309 octets) requiert au moins 3 paquets IP. Cela provoque une\n"
    "   fragmentation systématique sur les canaux UDP (QUIC, DNSSEC) et augmente le taux de perte de paquets.\n"
    "2. Latence TLS 1.3 : Lors de la négociation d'une poignée de main, le volume combiné des certificats\n"
    "   post-quantiques et des signatures dépasse la fenêtre de congestion initiale TCP (initcwnd = 10 MSS).\n"
    "   Cela contraint le serveur à attendre un Acknowledgment (ACK), ajoutant 1 RTT (Round-Trip Time) supplémentaire."
)
print("==================================================================")