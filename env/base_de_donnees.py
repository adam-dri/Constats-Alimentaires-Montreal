import sqlite3
import os

CHEMMIN_SQL = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "db", "db.sql"
)
CHEMIN_BD = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "db", "base_de_donnees.db"
)


class Database:
    def __init__(self):
        self.connexion = sqlite3.connect(CHEMIN_BD)
        self.connexion.row_factory = sqlite3.Row

    def get_connexion(self):
        return self.connexion

    def deconnecter(self):
        if self.connexion:
            self.connexion.close()

    # A1
    def creer_bd(self):
        """
        Crée les tables de la base de données si elles n'existent pas.
        """
        connexion = sqlite3.connect(CHEMIN_BD)
        curseur = connexion.cursor()
        curseur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name='contraventions';"
        )
        table_existe = curseur.fetchone()

        if table_existe:
            print("La table 'contraventions' existe déjà.")
        else:
            with open(CHEMMIN_SQL, "r", encoding="utf-8") as f:
                script_bd = f.read()
            curseur.execute(script_bd)
            connexion.commit()

        connexion.close()

    # A6
    def lister_etablissements(self):
        """
        Renvoie la liste des établissements, triée et sans doublons.

        Returns:
            list: Liste des noms d'établissements.
        """
        connexion = self.get_connexion()
        curseur = connexion.cursor()
        curseur.execute("""
            SELECT DISTINCT etablissement
            FROM contraventions
            ORDER BY etablissement
        """)
        lignes = [row['etablissement'] for row in curseur.fetchall()]
        connexion.close()
        return lignes

    # A2
    def rechercher_contraventions(
        self, etablissement=None, proprietaire=None, rue=None
    ):
        """
        Recherche des contraventions avec des critères optionnels.

        Args:
            etablissement (str, optional): Nom partiel de l'établissement.
            proprietaire (str, optional): Nom partiel du propriétaire.
            rue (str, optional): Nom partiel de la rue.

        Returns:
            list: Liste des contraventions correspondant aux critères.
        """
        connexion = self.get_connexion()
        curseur = connexion.cursor()

        requete = "SELECT * FROM contraventions WHERE 1=1"
        params = []

        if etablissement:
            requete += " AND etablissement LIKE ?"
            params.append(f"%{etablissement}%")
        if proprietaire:
            requete += " AND proprietaire LIKE ?"
            params.append(f"%{proprietaire}%")
        if rue:
            nom_rue = rue.split()
            for mot in nom_rue:
                requete += " AND adresse LIKE ?"
                params.append(f"%{mot}%")

        requete += " ORDER BY date DESC"

        curseur.execute(requete, params)
        contraventions = curseur.fetchall()

        connexion.close()
        return contraventions

    # A4
    def rechercher_contraventions_par_dates(self, date_debut, date_fin):
        """
        Recherche des contraventions entre deux dates.

        Args:
            date_debut (str): Date de début au format YYYY-MM-DD.
            date_fin (str): Date de fin au format YYYY-MM-DD.

        Returns:
            list: Liste des contraventions entre les deux dates.
        """
        connexion = self.get_connexion()
        curseur = connexion.cursor()

        requete = """
            SELECT * FROM contraventions
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC
        """
        curseur.execute(requete, (date_debut, date_fin))
        contraventions = curseur.fetchall()

        connexion.close()
        return contraventions

    # C1
    def statistiques_infractions(self):
        """
        Renvoie les statistiques des contraventions par établissement.

        Returns:
            list: Liste des établissements et le nombre de contraventions.
        """
        connexion = self.get_connexion()
        curseur = connexion.cursor()
        curseur.execute("""
            SELECT etablissement,
                   COUNT(*) AS nb
              FROM contraventions
             GROUP BY etablissement
             ORDER BY nb DESC
        """)
        resultats = curseur.fetchall()
        connexion.close()
        return resultats

    # C1 (un plus)
    def pire_etablissement(self):
        """
        Retourne l'établissement avec le plus de contraventions.

        Returns:
            tuple: Le nom de l'établissement et le nombre de contraventions.
        """
        connexion = self.get_connexion()
        curseur = connexion.cursor()
        curseur.execute("""
            SELECT etablissement, COUNT(*) AS nb
              FROM contraventions
             GROUP BY etablissement
             ORDER BY nb DESC
             LIMIT 1
        """)
        resultat = curseur.fetchone()
        connexion.close()
        return resultat

    # E1
    def creer_utilisateur(
        self, username, password_hash, salt, nom, prenom, photo_profil=None
    ):
        """
        Crée un nouvel utilisateur dans la base de données.

        Returns:
            int: L'ID de l'utilisateur créé, ou None en cas d'erreur.
        """
        try:
            curseur = self.connexion.cursor()
            curseur.execute("""
                INSERT INTO utilisateurs (username, password_hash,
                             salt, nom, prenom, photo_profil)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, password_hash, salt, nom, prenom, photo_profil))

            self.connexion.commit()
            return curseur.lastrowid
        except sqlite3.Error as e:
            print("Erreur lors de la création de l'utilisateur:", e)
            return None

    # E2
    def obtenir_utilisateur(self, nom_utilisateur):
        """
        Récupère les informations d'un utilisateur par son nom d'utilisateur.

        Returns:
            dict: Informations de l'utilisateur ou None si non trouvé.
        """
        try:
            curseur = self.connexion.cursor()
            curseur.execute("SELECT * FROM utilisateurs WHERE username=?",
                            (nom_utilisateur,))
            return curseur.fetchone()
        except sqlite3.Error as erreur:
            print("Erreur lors de la récupération de l'utilisateur:", erreur)
            return None

    # E2
    def ajouter_session(self, identifiant_session, nom_utilisateur):
        """
        Ajoute une session pour un utilisateur.

        Args:
            identifiant_session (str): L'ID de la session.
            nom_utilisateur (str): Le nom d'utilisateur.
        """
        try:
            curseur = self.connexion.cursor()
            curseur.execute("""
                INSERT INTO sessions (id_session, username)
                VALUES (?, ?)
            """, (identifiant_session, nom_utilisateur))
            self.connexion.commit()
        except sqlite3.Error as e:
            print("Erreur lors de l'ajout de la session:", e)

    # E2
    def supprimer_session(self, identifiant_session):
        """
        Supprime une session en fonction de son ID.

        Args:
            identifiant_session (str): L'ID de la session à supprimer.
        """
        try:
            curseur = self.connexion.cursor()
            curseur.execute("DELETE FROM sessions WHERE id_session=?",
                            (identifiant_session,))
            self.connexion.commit()
        except sqlite3.Error as e:
            print("Erreur lors de la suppression de la session:", e)

    # E2
    def ajout_photo_profil(self, nom_utilisateur, photo_profil):
        """
        Ajoute ou met à jour la photo de profil de l'utilisateur.

        Args:
            nom_utilisateur (str): Le nom d'utilisateur de la personne.
            photo_profil (bytes): Les données de l'image de profil.
        """
        try:
            curseur = self.connexion.cursor()
            curseur.execute("""
                UPDATE utilisateurs
                SET photo_profil = ?
                WHERE username = ?
            """, (photo_profil, nom_utilisateur))
            self.connexion.commit()
        except sqlite3.Error as e:
            print("Erreur lors de l'ajout de la photo de profil:", e)

    # E2
    def etablissements_par_ids(self, liste_ids):
        """
        Récupère les établissements correspondant aux IDs donnés.

        Returns:
            list: Liste des établissements correspondant aux IDs.
        """
        try:
            curseur = self.connexion.cursor()
            curseur.execute(
                f"""SELECT id_poursuite, etablissement
                FROM contraventions
                WHERE id_poursuite IN (
                    {','.join(['?'] * len(liste_ids))}
                )""",
                liste_ids
            )
            return curseur.fetchall()
        except sqlite3.Error as e:
            print("Erreur lors de la récupération des établissements:", e)
            return []

    # E2
    def ajout_etablissements_surveilles(self, nom_utilisateur, liste_ids):
        """
        Ajoute des établissements à la liste
        des établissements surveillés d'un utilisateur.

        Args:
            nom_utilisateur (str): Le nom de l'utilisateur.
            liste_ids (str): Liste des IDs des établissements surveillés.
        """
        try:
            curseur = self.connexion.cursor()
            curseur.execute("""
                UPDATE utilisateurs
                SET etablissements_surveilles = ?
                WHERE username = ?
            """, (liste_ids, nom_utilisateur))
            self.connexion.commit()
        except sqlite3.Error as e:
            print("Erreur lors de l'ajout des établissements surveillés:", e)
