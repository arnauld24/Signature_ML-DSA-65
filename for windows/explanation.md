# Exercice 28 — ML-DSA (FIPS 204)

Ce document explique les principales parties du script de l'exercice : la
préparation des fichiers, la génération des clés, la signature et sa
vérification, les tests de rejet, l'utilisation d'une chaîne de contexte et la
comparaison des profils ML-DSA.

ML-DSA est un algorithme de signature numérique post-quantique standardisé
dans FIPS 204. Il est issu de CRYSTALS-Dilithium.

## 1. Imports et fonction auxiliaire

### Modules utilisés

```python
import os
import subprocess
import pandas as pd
```

- `os` permet de manipuler des fichiers et de générer des octets aléatoires.
- `subprocess` permet de lancer OpenSSL depuis Python.
- `pandas` organise les résultats des comparaisons dans un tableau.

### Fonction `run_openssl`

```python
def run_openssl(cmd):
    """Exécute une commande OpenSSL et retourne le code de retour, stdout et stderr."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()
```

La fonction centralise l'exécution des commandes OpenSSL :

- `capture_output=True` récupère les sorties standard et d'erreur au lieu de
  les afficher directement dans le terminal.
- `text=True` renvoie les sorties sous forme de chaînes de caractères.
- `returncode` vaut généralement `0` en cas de succès et une valeur non nulle
  en cas d'échec.
- `strip()` retire les espaces et retours à la ligne au début et à la fin des
  sorties.

Le code de retour permet notamment de déterminer si une vérification de
signature a réussi ou si OpenSSL a rejeté le document.

## 2. Préparation du fichier de test

### Nettoyage des résultats précédents

```python
files_to_clean = [
    "document.bin",
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
```

Cette partie supprime les fichiers de test générés par l'exercice lors d'une
exécution précédente. Cela évite de confondre d'anciens résultats avec ceux de
l'exécution en cours.

> **Attention :** ne placez pas de fichiers importants dans le dossier courant
> sous l'un de ces noms : ils seront supprimés.

### Création d'un document binaire aléatoire

```python
with open("document.bin", "wb") as f:
    f.write(os.urandom(1024))
```

- `"wb"` ouvre le fichier en écriture binaire.
- `os.urandom(1024)` produit 1 024 octets aléatoires.
- `write()` enregistre ces octets dans `document.bin`.

Le fichier constitue un exemple de contenu binaire à signer. La signature
porte sur les octets du fichier ; le type ou l'extension du document n'est pas
important.

## 3. Question 1 — Signer et vérifier un fichier

### Génération d'une clé privée ML-DSA-65

```python
code, out, err = run_openssl(
    "openssl genpkey -algorithm ML-DSA-65 -out key_65.pem"
)
```

OpenSSL génère une clé privée ML-DSA-65 et l'enregistre dans `key_65.pem`.
ML-DSA-65 correspond au profil associé à la catégorie de sécurité NIST 3.

À haut niveau, la génération de clé utilise des valeurs aléatoires pour
construire la clé privée et les éléments publics correspondants. Les détails
mathématiques sont définis par la procédure `KeyGen_internal` de FIPS 204.

### Extraction de la clé publique

```python
code_pub, out_pub, err_pub = run_openssl(
    "openssl pkey -in key_65.pem -pubout -out pub_65.pem"
)
```

Cette commande dérive la clé publique correspondante et l'enregistre dans
`pub_65.pem`. La clé privée sert à signer ; la clé publique peut être partagée
et sert à vérifier les signatures.

### Signature du document

```python
code_sig, out_sig, err_sig = run_openssl(
    "openssl pkeyutl -sign -in document.bin -inkey key_65.pem -out sig_65.sig"
)
```

OpenSSL signe les octets de `document.bin` avec la clé privée, puis enregistre la
signature binaire dans `sig_65.sig`.

Dans les grandes lignes, ML-DSA calcule une valeur liée à la clé publique et au
message, forme un engagement à partir de valeurs éphémères, puis produit une
réponse qui satisfait les contrôles de la norme. Des tentatives qui ne
satisfont pas les bornes requises sont rejetées en interne avant que la
signature soit produite.

### Mesure de la taille de la signature

```python
sig_size_q1 = os.path.getsize("sig_65.sig")
```

`os.path.getsize()` renvoie la taille du fichier en octets. Une signature
ML-DSA-65 encodée par la spécification a une taille fixe de **3 309 octets**,
indépendamment de la taille du message signé.

### Vérification de la signature

```python
code_ver, out_ver, err_ver = run_openssl(
    "openssl pkeyutl -verify -in document.bin -sigfile sig_65.sig "
    "-pubin -inkey pub_65.pem"
)
```

OpenSSL vérifie que `sig_65.sig` correspond au contenu de `document.bin` et à la
clé publique `pub_65.pem`. Si la commande renvoie le code `0`, la vérification
a réussi. Un code non nul indique un échec.

## 4. Question 2 — Tester le rejet des entrées modifiées

### Test 2.1 — Modification du document

```python
with open("document.bin", "rb") as f:
    data = bytearray(f.read())

data[0] ^= 0xFF

with open("file_tampered.bin", "wb") as f:
    f.write(data)
```

Le fichier original est lu en mode binaire. `bytearray` permet de modifier les
octets ; l'opération `^= 0xFF` inverse les bits du premier octet. La copie
modifiée est écrite dans `file_tampered.bin`.

La vérification est ensuite exécutée avec le document altéré et la signature
originale :

```python
code_t1, _, err_t1 = run_openssl(
    "openssl pkeyutl -verify -in file_tampered.bin "
    "-sigfile sig_65.sig -pubin -inkey pub_65.pem"
)
```

La signature est liée au message original. Modifier le message conduit à un
résultat de vérification différent ; OpenSSL doit donc rejeter cette
combinaison. Le code de retour attendu est non nul.

### Test 2.2 — Utilisation d'une autre clé publique

```python
run_openssl("openssl genpkey -algorithm ML-DSA-65 -out key_other.pem")
run_openssl("openssl pkey -in key_other.pem -pubout -out pub_other.pem")
```

Ces commandes créent une nouvelle paire de clés indépendante. Le script
essaie ensuite de vérifier la signature originale avec `pub_other.pem` :

```python
code_t2, _, err_t2 = run_openssl(
    "openssl pkeyutl -verify -in document.bin "
    "-sigfile sig_65.sig -pubin -inkey pub_other.pem"
)
```

La signature ayant été créée avec la clé privée d'origine, elle ne doit pas
être validée par la clé publique d'une autre paire. Le code de retour attendu
est non nul.

### Test 2.3 — Troncature de la signature

```python
with open("sig_65.sig", "rb") as f:
    sig_raw = f.read()

with open("sig_truncated.sig", "wb") as f:
    f.write(sig_raw[:3000])
```

La signature est lue en binaire, puis seuls ses 3 000 premiers octets sont
écrits dans `sig_truncated.sig`. Il manque ainsi 309 octets par rapport à la
taille complète de 3 309 octets.

La signature tronquée n'a plus l'encodage complet attendu par ML-DSA. OpenSSL
doit échouer à la décoder ou à la vérifier et renvoyer un code non nul.

## 5. Question 3 — Chaîne de contexte

### Définition des contextes

```python
ctx_origin = "ENSPY_INFO_2026"
ctx_wrong = "ENSPY_AUTRE_CTX"
```

Une chaîne de contexte permet de distinguer les domaines d'utilisation d'une
signature. Elle doit être choisie par l'application et rester identique à la
signature et à la vérification.

### Signature avec un contexte

```python
run_openssl(
    f'openssl pkeyutl -sign -in document.bin -inkey key_65.pem '
    f'-out sig_ctx.sig -pkeyopt context-string:"{ctx_origin}"'
)
```

L'option `context-string` demande à OpenSSL de signer le message dans le
contexte `ENSPY_INFO_2026`.

Dans le mode ML-DSA pur, le contexte est encodé avec le message selon les
règles de séparation de domaine de FIPS 204. Le calcul associe ainsi la
signature au contexte utilisé, en plus du contenu du document et de la clé.

### Vérification avec le contexte correct puis incorrect

```python
code_c1, _, _ = run_openssl(
    f'openssl pkeyutl -verify -in document.bin -sigfile sig_ctx.sig '
    f'-pubin -inkey pub_65.pem -pkeyopt context-string:"{ctx_origin}"'
)

code_c2, _, _ = run_openssl(
    f'openssl pkeyutl -verify -in document.bin -sigfile sig_ctx.sig '
    f'-pubin -inkey pub_65.pem -pkeyopt context-string:"{ctx_wrong}"'
)
```

- `code_c1` doit être égal à `0` : le contexte correspond à celui utilisé à
  la signature.
- `code_c2` doit être différent de `0` : le contexte fourni à la vérification
  ne correspond pas.

Ce mécanisme aide à prévenir la réutilisation accidentelle d'une signature
dans un autre domaine applicatif, à condition que les applications définissent
et vérifient correctement leurs contextes.

## 6. Question 4 — Comparaison des profils ML-DSA

### Liste des profils

```python
algos = ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]
```

La boucle parcourt les trois profils normalisés. Pour chacun, le script génère
une paire de clés, signe le même fichier, mesure la taille de la clé publique
et de la signature, puis ajoute ces valeurs aux résultats.

| Profil | Paramètres du module (`k`, `ℓ`) | Catégorie de sécurité NIST |
|---|---:|---:|
| ML-DSA-44 | (4, 4) | 2 |
| ML-DSA-65 | (6, 5) | 3 |
| ML-DSA-87 | (8, 7) | 5 |

### Résultats de taille attendus

Les tailles ci-dessous correspondent aux encodages ML-DSA spécifiés. La taille
sur disque des clés au format PEM peut également dépendre de l'encapsulation
utilisée par OpenSSL.

| Profil | Clé publique (octets) | Signature (octets) |
|---|---:|---:|
| ML-DSA-44 | 1 312 | 2 420 |
| ML-DSA-65 | 1 952 | 3 309 |
| ML-DSA-87 | 2 592 | 4 627 |

`pandas.DataFrame(results)` transforme la liste de résultats en tableau, et
`to_string(index=False)` l'affiche sans colonne d'index.

## 7. Remarques sur l'impact réseau

### Taille des messages et MTU

Une signature ML-DSA dépasse la MTU Ethernet courante de 1 500 octets. Son
transport peut donc nécessiter plusieurs paquets ou segments. Le comportement
exact dépend du protocole utilisé, de la taille des données qui l'entourent et
de la gestion de la fragmentation par la pile réseau. Les mécanismes de
fragmentation et les pertes éventuelles peuvent affecter la fiabilité du
transport, en particulier dans certains usages UDP.

### Taille des échanges TLS

Une clé publique ou une signature plus volumineuse augmente la taille des
données échangées pendant une négociation TLS, notamment lorsque des
certificats sont transmis. Selon la taille totale de la chaîne de certificats,
la configuration réseau et la fenêtre de congestion disponible, davantage de
segments ou un aller-retour supplémentaire peuvent être nécessaires. L'effet
réel sur la latence dépend donc du contexte de déploiement.
