# Projet ML-DSA

Ce projet présente les signatures numériques post-quantiques ML-DSA (FIPS 204)
avec OpenSSL. Les scripts génèrent et vérifient des signatures, testent le rejet
de messages altérés et comparent les profils ML-DSA-44, ML-DSA-65 et ML-DSA-87.

## Prérequis

- Python 3
- OpenSSL 3.5 ou version ultérieure avec la prise en charge de ML-DSA
- `pandas` pour les scripts qui affichent des tableaux comparatifs

OpenSSL est un programme système distinct : son installation n'est pas incluse
dans celle de Python. Vérifiez la disponibilité de Python avec `py --version`
et celle d'OpenSSL avec `openssl version`. Pour voir les algorithmes connus de
votre installation, exécutez :

```powershell
openssl list -signature-algorithms
```

La sortie doit contenir ML-DSA-44, ML-DSA-65 et ML-DSA-87.

## Créer l'environnement Python sous Windows

Exécutez les commandes suivantes depuis le dossier racine du projet, qui
contient ce README :

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pandas
```

Si PowerShell bloque l'activation, autorisez-la uniquement pour le processus
PowerShell en cours, puis activez l'environnement :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Vérifiez que `pandas` est installé :

```powershell
python -c "import pandas; print(pandas.__version__)"
```

Pour quitter l'environnement virtuel :

```powershell
deactivate
```

## Configurer OpenSSL

`exercise_28.py` exécute OpenSSL avec le nom `openssl`. Le dossier `bin`
d'OpenSSL doit donc être ajouté à la variable d'environnement `PATH`.

Les scripts `comparaison.py`, `evaluation.py`, `modification.py` et
`signature.py` définissent une constante `OPENSSL_PATH` qui pointe vers un
emplacement Windows précis. Si OpenSSL est installé ailleurs, modifiez cette
constante dans chacun de ces scripts. Exemple :

```python
OPENSSL_PATH = r"C:\Program Files\OpenSSL-Win64\bin\openssl.exe"
```

Remplacez ce chemin par l'emplacement réel sur votre ordinateur. Ces scripts
utilisent le chemin configuré à la place du nom `openssl`.

## Exécuter l'exercice principal

Activez l'environnement depuis le dossier racine, puis lancez le script depuis
le dossier `ml_dsa` :

```powershell
.\.venv\Scripts\Activate.ps1
Set-Location .\ml_dsa
python .\exercise_28.py
```

Le script crée un fichier aléatoire `file.bin` de 1 024 octets, génère une
paire de clés ML-DSA-65, signe et vérifie le fichier, puis teste le rejet d'un
message modifié, d'une autre clé et d'une signature tronquée. Il vérifie aussi
les chaînes de contexte et affiche les tailles des clés publiques et des
signatures pour les trois profils ML-DSA.

## Exécuter les autres scripts

Les autres scripts utilisent des chemins relatifs : lancez-les depuis le
dossier `ml_dsa`. Ils nécessitent aussi `document.bin` et, selon le script, des
clés et une signature. Pour préparer ces fichiers avec OpenSSL :

```powershell
# Placez le fichier à tester dans ce dossier sous le nom document.bin
openssl genpkey -algorithm ML-DSA-65 -out key_65.pem
openssl pkey -in key_65.pem -pubout -out pub_65.pem
openssl pkeyutl -sign -in document.bin -inkey key_65.pem -out sig_65.sig
```

Vous pouvez aussi réutiliser le fichier créé par `exercise_28.py` en le
copiant sous le nom attendu :

```powershell
Copy-Item .\file.bin .\document.bin
```

Lancez ensuite le script voulu, par exemple :

```powershell
python .\comparaison.py
```

Les sections suivantes décrivent les entrées et le rôle de chaque script.

## Description des fichiers Python

### `ml_dsa/exercise_28.py`

Script principal de l'exercice, recommandé pour commencer.

- Importe `os` pour manipuler les fichiers et produire les données aléatoires,
  `subprocess` pour lancer les commandes OpenSSL et `pandas` pour créer le
  tableau de résultats.
- La fonction `run_openssl()` exécute une commande OpenSSL et renvoie son code
  de retour, sa sortie standard et sa sortie d'erreur.
- Supprime les fichiers existants correspondant aux noms prévus par le
  nettoyage de l'exercice, puis crée `file.bin` avec 1 024 octets aléatoires.
  Ne conservez pas de fichiers importants portant ces noms dans le dossier
  courant.
- Génère une clé privée ML-DSA-65 et la clé publique correspondante, signe le
  fichier, mesure la taille de la signature et la vérifie.
- Vérifie que le programme rejette un fichier modifié, une autre clé publique
  et une signature tronquée.
- Signe avec une chaîne de contexte, vérifie avec cette même chaîne, puis
  vérifie qu'une chaîne différente entraîne le rejet.
- Génère des clés et signatures ML-DSA-44, ML-DSA-65 et ML-DSA-87, mesure leurs
  tailles et affiche les résultats ainsi que des remarques sur l'impact réseau.

### `ml_dsa/comparaison.py`

Compare les tailles des clés publiques et des signatures pour les trois
profils ML-DSA. Le script lit `document.bin`, appelle OpenSSL à l'aide de
`OPENSSL_PATH`, rassemble les mesures dans un tableau `pandas` et supprime les
clés et signatures temporaires créées. Il affiche également des remarques sur
l'impact réseau.

### `ml_dsa/evaluation.py`

Compare également les tailles des profils ML-DSA-44, ML-DSA-65 et ML-DSA-87 à
partir de `document.bin`, de `OPENSSL_PATH` et d'un tableau `pandas`. Cette
comparaison et les remarques sur l'impact réseau recoupent largement celles
de `comparaison.py`.

### `ml_dsa/modification.py`

Montre les échecs de vérification en modifiant un octet de `document.bin`, en
créant une seconde paire de clés ML-DSA-65 et en tronquant `sig_65.sig`. Le
script vérifie ces cas avec OpenSSL et affiche si chacun est rejeté. Il
nécessite le document original, la signature et la clé publique, et utilise
`OPENSSL_PATH`.

### `ml_dsa/signature.py`

Vérifie la signature existante `sig_65.sig` avec `document.bin` et `pub_65.pem`,
puis affiche le résultat. Les commandes de génération des clés et de signature
sont commentées : ces fichiers doivent donc être préparés avant l'exécution.
Le script utilise `OPENSSL_PATH`.

### `binary_file.py`

Ce script situé à la racine du projet est une expérience indépendante de
génération de fichier. Il importe `os`, `subprocess` et `pandas`, supprime une
liste de fichiers de test, puis écrit 1 024 octets aléatoires dans
`document.dat`. Il tente ensuite de mesurer la taille de `document.bin`, qu'il
ne crée pas : il peut donc provoquer une erreur `FileNotFoundError` si ce
fichier n'existe pas déjà. Les modules `subprocess` et `pandas` ne sont pas
utilisés dans la version actuelle. Avant de le lancer, vérifiez sa liste de
nettoyage : tout fichier correspondant dans le dossier courant sera supprimé.

## Explications existantes

`explanation.md` et `esplanation1.md` contiennent les explications d'origine
sur l'exercice, le fonctionnement de ML-DSA, les tests de rejet, les chaînes de
contexte et les comparaisons de tailles. Les descriptions ci-dessus résument
les fichiers Python dans leur état actuel.

## Fichiers générés et sécurité

Les scripts créent des clés privées, des clés publiques, des signatures et des
fichiers de test dans leur dossier de travail. Le fichier `.gitignore` à la
racine exclut l'environnement virtuel et les fichiers de test générés. Ne
publiez pas de clé privée ni de document contenant des informations sensibles.
