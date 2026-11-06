import os
import subprocess
import pandas as pd


def run_openssl(cmd):
    """Exécute une commande OpenSSL et retourne le code de retour, stdout et stderr."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

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
    run_cmd(f"openssl genpkey -algorithm {algo} -out {kfile}")
    run_cmd(f"openssl pkey -in {kfile} -pubout -out {pfile}")
    run_cmd(f"openssl pkeyutl -sign -in document.bin -inkey {kfile} -out {sfile}")

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