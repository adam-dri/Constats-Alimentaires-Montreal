import base_de_donnees
import sqlite3
import requests
import csv
from io import StringIO


def A1():
    """
    Récupère les contraventions depuis une URL, analyse le fichier CSV,
    et met à jour la table 'contraventions' de la base de données SQLite
    en évitant les doublons selon l'ID de poursuite.

    Cette fonction télécharge les données de contraventions,
    vérifie si elles sont déjà présentes
    dans la base de données, et les insère si elles ne sont pas en doublon.

    Returns:
        str: Message d'erreur si le téléchargement échoue, sinon rien.
    """

    URL_CONTRAVENTION = (
        "https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9-5955efeb91a0"
        "/resource/7f939a08-be8a-45e1-b208-d8744dca8fc6/"
        "download/violations.csv"
    )

    response = requests.get(URL_CONTRAVENTION)
    response.encoding = "utf-8"

    if response.status_code != 200:
        return f"Erreur lors du téléchargement du CSV : {response.status_code}"

    contenu = response.text
    fichier = StringIO(contenu)
    reader = csv.DictReader(fichier)

    connexion = sqlite3.connect(base_de_donnees.CHEMIN_BD)
    curseur = connexion.cursor()

    requete_verif = "SELECT COUNT(*) FROM contraventions WHERE id_poursuite=?"
    requete = """
    INSERT INTO contraventions (
        id_poursuite, business_id, date, description,
        adresse, date_jugement, etablissement,
        montant, proprietaire, ville,
        statut, date_statut, categorie
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    num_ligne = 0
    for i in reader:
        id_poursuite = int(i["id_poursuite"])

        curseur.execute(requete_verif, (id_poursuite,))
        if curseur.fetchone()[0] == 0:
            try:
                id_poursuite = int(i["id_poursuite"])
                business_id = int(i["business_id"])
                date = i["date"]
                description = i["description"]
                adresse = i["adresse"]
                date_jugement = i["date_jugement"]
                etablissement = i["etablissement"]
                montant = i["montant"]
                proprietaire = i["proprietaire"]
                ville = i["ville"]
                statut = i["statut"]
                date_statut = i["date_statut"]
                categorie = i["categorie"]

                curseur.execute(
                    requete,
                    (
                        id_poursuite, business_id, date, description,
                        adresse, date_jugement, etablissement, montant,
                        proprietaire, ville, statut, date_statut, categorie
                    )
                )
                num_ligne += 1

            except Exception as e:
                print(f"""Erreur lors de l'insertion
                       de la ligne suivante : {num_ligne}""")
                print("Erreur :", e)

    connexion.commit()
    connexion.close()
