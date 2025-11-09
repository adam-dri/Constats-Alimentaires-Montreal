# Installation et tests - Constats Alimentaires Montréal

Guide d'installation et de test de l'application.

## Prérequis

- Python 3.8+
- pip
- SQLite3

## Installation

### 1. Cloner le projet
```bash
git clone https://github.com/adam-dri/Constats-Alimentaires-Montreal.git
cd Constats-Alimentaires-Montreal/env
```

### 2. Créer l'environnement virtuel
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration
```bash
echo 'SECRET_KEY=VOTRE_CLE_ICI' >> Constats-Alimentaires-Montreal/env/.env
```

### 5. Initialiser la base de données
```bash
python init_projet.py
```

Cette commande télécharge les données de la Ville de Montréal et les importe dans la base SQLite.

**Vérifier l'import :**
```bash
sqlite3 db/base_de_donnees.db "SELECT COUNT(*) FROM contraventions;"
```

### 6. Lancer l'application
```bash
source env/bin/activate
python -m flask run
```

Application accessible sur `http://localhost:5000`

---

## Tests des fonctionnalités

### A1 - Import des données

**Fonction testée :** `fonctionnalites.A1()` dans `init_projet.py`

**Test :**
```bash
python init_projet.py
sqlite3 db/base_de_donnees.db "SELECT COUNT(*) FROM contraventions;"
```

**Résultat attendu :** Environ 40 000+ enregistrements

---

### A2 - Recherche par critères

**Fonctions testées :**
- Route Flask `resultats_recherche()` dans `app.py`
- Méthode `Database.rechercher_contraventions()` dans `base_de_donnees.py`

**Test :**
1. Dans Recherche de contraventions, rechercher un établissement grâce à :
   - Nom de l'établissement
   - Propriétaire
   - Rue

---

### A3 - Mise à jour automatique

**Fonctions testées :**
- `mise_a_jour_db()` dans `app.py`
- `maj_minuit()` dans `app.py`

**Test :**

Pour tester la modification, modifier `cron` en `hour='*', minute='*'` et regarder la console : la fonction `mise_a_jour_db` doit s'exécuter chaque minute.

---

### A4 - API REST par dates

**Fonctions testées :**
- Route Flask `api_contraventions_par_dates()` dans `app.py`
- Méthode `Database.rechercher_contraventions_par_dates()` dans `base_de_donnees.py`
- Route Flask `documentation()` pour `/doc`

**Test :**
```bash
curl "http://localhost:5000/contrevenants?du=2025-01-01&au=2025-02-01"
```

Vérifier que toutes les dates dans la réponse sont dans l'intervalle demandé.

---

### A5 - Recherche AJAX par période

**Fonction testée :** `rechercheDates()` dans `static/js/validations.js`

**Test :**
1. Sur la page d'accueil, choisir deux dates
2. Cliquer sur "Rechercher" → le JS appelle `/contrevenants` et affiche un tableau

---

### A6 - Infractions par établissement

**Fonctions testées :**
- Route Flask `api_lister_etablissements()` dans `app.py`
- Route Flask `api_infractions_par_etablissement()` dans `app.py`
- `chargerListeEtablissements()` et `rechercherParEtablissement()` dans `static/js/validations.js`

**Test :**
1. Vérifier que le `<select>` se remplit via `chargerListeEtablissements()`
2. Sélectionner un établissement et cliquer → `rechercherParEtablissement()` affiche le tableau

---

### C1 - Statistiques JSON

**Fonctions testées :**
- Route Flask `obtenir_statistiques()` dans `app.py`
- Méthode `Database.statistiques_infractions()` dans `base_de_donnees.py`

**Test :**
```bash
curl "http://localhost:5000/statistiques"
```

---

### C2 - Statistiques XML

**Fonction testée :** Route Flask `obtenir_statistiques_xml()` dans `app.py`

**Test :**
```bash
curl -i "http://localhost:5000/statistiques/xml"
```

---

### C3 - Statistiques CSV

**Fonction testée :** Route Flask `obtenir_statistiques_csv()` dans `app.py`

**Test :**
```bash
curl -i "http://localhost:5000/statistiques/csv"
```

---

### E1 - Création de profil

**Fonctions testées :**
- Route Flask `creer_utilisateur_api()` dans `app.py`
- Schéma JSON `schemas/utilisateur_schema.json`
- Méthode `Database.creer_utilisateur()` dans `base_de_donnees.py`

**Test :**
```bash
curl -X POST http://127.0.0.1:5000/api/utilisateurs \
  -H "Content-Type: application/json" \
  -d '{"username":"adam-test","password":"MotDePasse123","nom":"test","prenom":"adam"}'
```

Recevoir `{"message":"Utilisateur créé avec succès"}` ou un message d'erreur si le JSON n'est pas valide.

---

### E2 - Inscription et profil

**Fonctions testées :**
- Route Flask `inscription()` dans `app.py`
- Route Flask `connexion()` dans `app.py`
- Route Flask `deconnexion()` dans `app.py`
- Route Flask `profil()` dans `app.py`
- Route Flask `televerser_photo()` dans `app.py`
- Route Flask `rechercher_etablissements()` dans `app.py`
- Route Flask `etablissements_surveilles()` dans `app.py`

**Test :**
1. Créer un compte via `/inscription`
2. Se connecter via `/connexion`
3. Aller sur `/profil`, téléverser une photo (`televerser_photo()`) et vérifier qu'elle s'affiche
4. Ajouter des établissements surveillés (`etablissements_surveilles()` et `rechercher_etablissements()`) et revenir sur la page pour voir la liste

---

## Endpoints API

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/contrevenants?du=DATE&au=DATE` | GET | Contraventions par période |
| `/etablissements` | GET | Liste des établissements |
| `/infractions?etablissement=NOM` | GET | Infractions par établissement |
| `/statistiques` | GET | Statistiques JSON |
| `/statistiques/xml` | GET | Statistiques XML |
| `/statistiques/csv` | GET | Statistiques CSV |
| `/api/utilisateurs` | POST | Création d'utilisateur |
| `/doc` | GET | Documentation API |

## Documentation API interactive

Une fois l'application lancée : `http://localhost:5000/doc`