## Correction du projet INF5190 – Programmation web avancée

Pour chaque point, j’indique les fonctions Python (et JS) utilisées.

Étapes pour lancer le projet
- source env/bin/activate
- python -m flask run

---

### A1 – Import des données (10 XP)

**Fonction utilisée :**  
- `fonctionnalites.A1()` dans **init_projet.py**

**Cloner :**
1. git clone https://github.com/adam-dri/Constats-Alimentaires-Montreal.git
2. cd Constats-Alimentaires-Montreal/env
3. python3 -m venv .venv
4. source .venv/bin/activate
5. pip install -r requirements.txt
6. echo 'SECRET_KEY=VOTRE_CLE_ICI' >> Constats-Alimentaires-Montreal/env/.env

---

**Tester :**
1. Lance l’import :
   ```bash
   python init_projet.py
   ```
2. Vérifie le nombre d’enregistrements :  
   ```bash
   sqlite3 db/base_de_donnees.db "SELECT COUNT(*) FROM contraventions;"
   ```

---

### A2 – Recherche par critères (10 XP)

**Fonctions utilisées :**  
- Route Flask `resultats_recherche()` dans **app.py**  
- Méthode `Database.rechercher_contraventions()` dans **base_de_donnees.py**

**Tester :**
1. Dans Recherche de contraventions, rechercher un établissement grace à :
- Nom de l'établissement
- Propriétaire
- Rue

---

### A3 – Mise à jour automatique (5 XP)

**Fonctions utilisées :**  
- `mise_a_jour_db()` dans **app.py** 
- `maj_minuit()` dans **app.py**

**Tester :**
- Pour tester la modification, modifier `cron` en `hour='*', minute='*'` et regarder la console : la fonction `mise_a_jour_db` doit s’exécuter chaque minute.

---

### A4 – API REST par dates (10 XP)

**Fonctions utilisées :**  
- Route Flask `api_contraventions_par_dates()` dans **app.py** 
- Méthode `Database.rechercher_contraventions_par_dates()` dans `**base_de_donnees.py**
- Route Flask `documentation()` pour **/doc**

**Tester :**
```bash
curl "http://localhost:5000/contrevenants?du=2025-01-01&au=2025-02-01"
```
Vérifier que toutes les dates dans la réponse sont dans l’intervalle demandé.

---

### A5 – Recherche AJAX par période (10 XP)

**Fonction JS utilisée :**  
- `rechercheDates()` dans **static/js/validations.js**

**Tester :**
1. Sur la page d’accueil, choisir deux dates  
2. Cliquer sur “Rechercher” → le JS appelle `/contrevenants` et affiche un tableau

---

### A6 – Infractions par établissement (10 XP)

**Fonctions utilisées :**  
- Route Flask `api_lister_etablissements()` dans **app.py**
- Route Flask `api_infractions_par_etablissement()` dans **app.py**
- `chargerListeEtablissements()` et `rechercherParEtablissement()` dans **static/js/validations.js**

**Tester :**
1. Vérifier que le `<select>` se remplit via `chargerListeEtablissements()`  
2. Sélectionner un établissement et cliquer → `rechercherParEtablissement()` affiche le tableau

---

### C1 – Statistiques JSON (10 XP)

**Fonctions utilisées :**  
- Route Flask `obtenir_statistiques()` dans **app.py**
- Méthode `Database.statistiques_infractions()` dans **base_de_donnees.py**

**Tester :**
```bash
curl "http://localhost:5000/statistiques"
```

---

### C2 – Statistiques XML (5 XP)

**Fonctions utilisées :**  
- Route Flask `obtenir_statistiques_xml()` dans **app.py**

**Tester :**
```bash
curl -i "http://localhost:5000/statistiques/xml"
```

---

### C3 – Statistiques CSV (5 XP)

**Fonctions utilisées :**  
- Route Flask `obtenir_statistiques_csv()` dans **app.py**

**Tester :**
```bash
curl -i "http://localhost:5000/statistiques/csv"
```

---

### E1 – Création de profil (15 XP)

**Fonctions utilisées :**  
- Route Flask `creer_utilisateur_api()` dans **app.py**
- Schéma JSON `schemas/utilisateur_schema.json`  
- Méthode `Database.creer_utilisateur()` dans **base_de_donnees.py**

**Tester :**
```bash
curl -X POST http://127.0.0.1:5000/api/utilisateurs \
  -H "Content-Type: application/json" \
  -d '{"username":"adam-test","password":"MotDePasse123","nom":"test","prenom":"adam"}'

```
- Recevoir `{"message":"Utilisateur cr\u00e9\u00e9 avec succ\u00e8s"}` ou un message d’erreur si le JSON n’est pas valide.

---

### E2 – Inscription et profil (15 XP)

**Fonctions utilisées :**  
- Route Flask `inscription()` dans **app.py**  
- Route Flask `connexion()` dans **app.py**
- Route Flask `deconnexion()` dans **app.py**
- Route Flask `profil()` dans **app.py**
- Route Flask `televerser_photo()` dans **app.py**
- Route Flask `rechercher_etablissements()` dans **app.py**
- Route Flask `etablissements_surveilles()` dans **app.py**

**Tester :**
1. Créer un compte via `/inscription`  
2. Se connecter via `/connexion`  
3. Aller sur `/profil`, téléverser une photo (`televerser_photo()`) et vérifier qu’elle s’affiche  
4. Ajouter des établissements surveillés (`etablissements_surveilles()` et `rechercher_etablissements()`) et revenir sur la page pour voir la liste

---
**Total : 105 XP**
