# Constats Alimentaires Montréal

Application web pour consulter et analyser les données d'inspections sanitaires des établissements alimentaires de la Ville de Montréal.

## À propos

Cette application permet d'accéder facilement aux données ouvertes de la Ville de Montréal concernant les constats d'infraction lors d'inspections alimentaires. Elle offre une API REST et une interface web pour rechercher, consulter et surveiller les établissements.

## Fonctionnalités

- Recherche de contraventions par établissement, propriétaire, rue ou période
- API REST avec exports JSON, XML et CSV
- Statistiques des infractions par établissement
- Système d'authentification utilisateur
- Surveillance personnalisée d'établissements
- Mise à jour automatique quotidienne des données
- Interface web avec recherche AJAX dynamique

## Technologies

- Python, Flask
- SQLite
- JavaScript
- APScheduler
- JSON Schema

## Installation

Voir [INSTALLATION.md](INSTALLATION.md) pour les instructions détaillées d'installation et de test.

## Structure du projet
```
├── app.py                  # Routes Flask
├── base_de_donnees.py      # Accès aux données
├── fonctionnalites.py      # Logique métier
├── init_projet.py          # Initialisation
├── db/                     # Base de données
├── schemas/                # Validation JSON
├── static/                 # CSS et JavaScript
└── templates/              # Templates HTML
```

## Documentation

- [INSTALLATION.md](INSTALLATION.md) - Installation et tests
- [API Documentation](http://localhost:5000/doc) - Documentation RAML

## Licence

MIT

## Source des données

[Ville de Montréal - Données Ouvertes](https://donnees.montreal.ca/)

## Auteur

**Adam Driouich**  
[LinkedIn](https://linkedin.com/in/adam-driouich) • [GitHub](https://github.com/adam-dri)