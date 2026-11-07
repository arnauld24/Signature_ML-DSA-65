# Guide d'utilisation du programme ML-DSA

Ce projet permet de générer des clés ML-DSA, signer des fichiers, vérifier des signatures et exécuter les scripts de démonstration de la signature post-quantique avec OpenSSL.

## Prérequis

Avant de lancer le programme, vérifiez que vous avez :

- Python 3 installé
- OpenSSL installé et disponible dans le PATH
- Tkinter installé pour l’interface graphique
- pandas pour les scripts qui affichent des tableaux comparatifs
- Hex Editor (Extension VS Code) pour visualiser les fichier binaire

### Vérification d’OpenSSL

Dans un terminal, exécutez :

OpenSSL est un programme système distinct : son installation n'est pas incluse
dans celle de Python. Vérifiez la disponibilité de Python avec `py --version`
et celle d'OpenSSL avec `openssl version`. Pour voir les algorithmes connus de
votre installation, exécutez

```bash
openssl list -signature-algorithms
```

La sortie doit contenir ML-DSA-44, ML-DSA-65 et ML-DSA-87.

### 1. Créer l'environnement Python sous une distribution Linux

Exécutez les commandes suivantes depuis le dossier racine du projet, qui
contient ce README :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pandas
```
Vérifiez que `pandas` est installé :

```bash
python -m pip show pandas
```
Pour quitter l'environnement virtuel :

```bash
deactivate
```

### 2. Vérification de Tkinter

### 2.1. Installation de Tkinter sous Linux

```bash
sudo apt update
sudo apt install python3-tk
```

### 2.2. Vérification de Tkinter sous Linux

```bash
python3 -c "import tkinter; print('Tkinter OK')"
```

Si cela fonctionne, l’interface graphique peut s’ouvrir.

---

#### Lancer l’interface graphique

Depuis le dossier du projet, exécutez :

```bash
python3 interface.py
```

Vous verrez une interface avec :

- une liste de scripts du projet
- des champs pour choisir le document, la clé privée, la clé publique et la signature
- des boutons pour générer des clés, générer un fichier binaire, signer et vérifier
- une zone de sortie qui affiche les commandes exécutées et leur durée

---

#### Utilisation de l’interface

#### 1. Générer un fichier binaire

Cliquez sur :

- Générer fichier binaire

Cela crée un fichier aléatoire de 1024 octets dans le chemin du champ "Fichier à signer".

Par défaut, le chemin est :

```text
document.bin
```

---

#### 2. Générer une paire de clés

Cliquez sur :

- Générer paire de clés

Le programme exécute :

```bash
openssl genpkey -algorithm ML-DSA-65 -out key_65.pem
openssl pkey -in key_65.pem -pubout -out pub_65.pem
```

Les fichiers générés sont :

- `key_65.pem` : clé privée
- `pub_65.pem` : clé publique

Vous pouvez modifier le chemin dans l’interface si vous souhaitez enregistrer les fichiers ailleurs.

---

#### 3. Signer un fichier

1. Sélectionnez le fichier à signer dans le champ "Fichier à signer"
2. Vérifiez que la clé privée est correcte dans le champ "Clé privée"
3. Vérifiez le chemin de sortie dans "Signature de sortie"
4. Cliquez sur "Signer le fichier"

Le programme lance la commande :

```bash
openssl pkeyutl -sign -in document.bin -inkey key_65.pem -out signed_document_65.sig
```

Par défaut, la signature est enregistrée sous :

```text
signed_document_65.sig
```

---

#### 4. Vérifier une signature

1. Sélectionnez le document original
2. Sélectionnez le fichier de signature
3. Sélectionnez la clé publique correspondante
4. Cliquez sur "Vérifier la signature"

Le programme exécute :

```bash
openssl pkeyutl -verify -in document.bin -sigfile signed_document_65.sig -pubin -inkey pub_65.pem
```

Si la vérification réussit, OpenSSL retourne un statut de succès.

---

## Lancer les scripts du projet directement

La liste de gauche contient les scripts de démonstration du projet :

- `exercise_28.py`
- `comparaison.py`
- `evaluation.py`
- `modification.py`
- `signature.py`
- `binary_file.py`

Cliquez sur l’un d’eux pour le lancer dans le même environnement à partir de l’interface.

---

## Exemple complet de test

1. Générer un document binaire
2. Générer une paire de clés ML-DSA-65
3. Signer le document
4. Vérifier la signature
5. Lancer un des scripts de démonstration du projet

Exemple de séquence :

```bash
python3 interface.py
```

puis dans l’interface :

- Générer fichier binaire
- Générer paire de clés
- Signer le fichier
- Vérifier la signature

---

## Remarques importantes

- Les scripts du projet utilisent OpenSSL via des commandes shell.
- Vous devez avoir un support ML-DSA dans votre version d’OpenSSL.
- Les fichiers générés sont créés dans le dossier du projet.
- Il faut être prudent avec les clés privées et les signatures, car elles sont sensibles (un confusion et la vérification échoue).

---

## Démarrage rapide

```bash
cd /chemin/vers/le/projet
python3 interface.py
```

puis :

- Générer fichier binaire
- Générer paire de clés
- Signer le fichier
- Vérifier la signature

---

## Résumé

Ce programme est un outil visuel pour démontrer la signature numérique ML-DSA avec OpenSSL. Il permet de :

- générer des fichiers aléatoires
- créer des clés publiques et privées ML-DSA
- signer un fichier
- vérifier une signature
- lancer les scripts de démonstration du projet
- afficher les résultats dans une console intégrée
