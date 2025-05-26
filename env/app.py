import fonctionnalites
import base_de_donnees

from flask import (
    Flask, render_template,
    request, g,
    make_response, jsonify,
    session, redirect,
    url_for, flash,
    send_file
)

import sqlite3
import csv
import io
import json
import xml.etree.ElementTree
from datetime import date
import hashlib
import uuid
import re
from functools import wraps
import os
from dotenv import load_dotenv


from apscheduler.schedulers.background import BackgroundScheduler
from jsonschema import validate, ValidationError


load_dotenv()

app = Flask(__name__)
SECRET = os.getenv("SECRET_KEY")
if not SECRET:
    raise RuntimeError("La variable SECRET_KEY n'est pas définie !")
app.secret_key = SECRET


def get_db():
    """
    Ouvre une connexion SQLite et la stocke dans 'g', si nécessaire.

    Returns:
        base_de_donnees.Database: objet de connexion à la base SQLite.
    """
    db = getattr(g, '_database', None)
    if db is None:
        g._database = base_de_donnees.Database()
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    """
    Ferme la connexion à la base de données en fin de requête.
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.deconnecter()


# A3
def mise_a_jour_db():
    """
    Met à jour la base de données en appelant la fonction A1.
    Utilisé pour la planification des mises à jour quotidiennes.
    """
    try:
        fonctionnalites.A1()
        print("Mise à jour de la base de données réussie.")
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la base de données : {e}")


# A3
scheduler = BackgroundScheduler()


def maj_minuit():
    """
    Démarre un planificateur pour exécuter la mise à jour
    de la base de données à minuit chaque jour.
    """
    try:
        scheduler.add_job(mise_a_jour_db, "cron", hour=0, minute=0)
        scheduler.start()
        print("Scheduler démarré. Prochaine exécution à 00h00.")
        print("Mise à jour testée avec succès.")
    except Exception as e:
        print(f"Erreur : {e}")


# A3
@app.teardown_appcontext
def teardown_appcontext(exception=None):
    """
    Ferme la connexion à la base de données et arrête le scheduler
    à la fin de la requête.
    """
    db = get_db()
    if db is not None:
        db.deconnecter()

    if scheduler.running:
        scheduler.shutdown()


# Connexion requise
def connexion_requise(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "utilisateur" not in session:
            return redirect(url_for("connexion"))
        return f(*args, **kwargs)
    return wrapper


@app.route("/")
def accueil():
    """
    Route d'accueil de l'application.
    """
    today = date.today().isoformat()
    return render_template("accueil.html", today=today)


# A2
@app.route("/recherche", methods=["POST"])
def resultats_recherche():
    """
    Route qui traite la recherche de contraventions via un formulaire.
    Interroge la base de données avec les critères saisis
    et affiche les résultats.

    - bash 'curl -i http://127.0.0.1:5000/recherche'

    Returns:
        str: Contenu HTML de la page de résultats ou message
        d'erreur en cas de problème.
    """
    db = get_db()

    etablissement = request.form.get("etablissement", "").strip()
    proprietaire = request.form.get("proprietaire", "").strip()
    rue = request.form.get("rue", "").strip()

    try:
        contraventions = db.rechercher_contraventions(
            etablissement=etablissement,
            proprietaire=proprietaire,
            rue=rue
        )
        return render_template("resultats.html", contraventions=contraventions)
    except sqlite3.Error as e:
        return (
            "Une erreur est survenue lors de la recherche. "
            "Veuillez réessayer plus tard."
        ), 500


# A4
@app.route("/contrevenants", methods=["GET"])
def api_contraventions_par_dates():
    """
    Service REST GET /contrevenants?du=YYYY-MM-JJ&au=YYYY-MM-JJ.
    Retourne un JSON listant toutes les contraventions entre les deux dates.

    - bash 'curl -i http://127.0.0.1:5000/contrevenants?du=YYYY-MM-JJ&au='
    'YYYY-MM-JJ'

    Returns:
        Response: Réponse JSON contenant les contraventions ou une erreur.
    """
    date_debut = request.args.get("du", "").replace("-", "")
    date_fin = request.args.get("au", "").replace("-", "")

    if not date_debut or not date_fin:
        return jsonify({
            "erreur": "Les paramètres 'du' et 'au' sont obligatoires"
        }), 400

    try:
        db = get_db()
        contraventions = db.rechercher_contraventions_par_dates(
            date_debut, date_fin)
        # Conversion de chaque Row en dictionnaire
        resultats_json = [dict(c) for c in contraventions]
        return jsonify(resultats_json), 200
    except Exception as e:
        return jsonify({
            "erreur": f"Impossible de récupérer les données : {e}"
        }), 500


# A4
@app.route("/doc")
def documentation():
    """
    Affiche la documentation HTML générée à partir du RAML.

    - bash 'curl -i http://127.0.0.1:5000/doc'
    """
    return render_template("doc.html")


# A6
@app.route("/etablissements", methods=["GET"])
def api_lister_etablissements():
    """
    Route API pour lister tous les établissements.

    - bash 'curl -i http://127.0.0.1:5000/etablissements'

    Returns:
        Response: Réponse JSON contenant les noms des établissements.
    """
    db = get_db()
    noms = db.lister_etablissements()
    return jsonify(noms), 200


# A6
@app.route("/infractions", methods=["GET"])
def api_infractions_par_etablissement():
    """
    Récupère les contraventions d'un établissement donné.

    Le paramètre 'etablissement' doit être fourni dans la requête.
    Retourne une liste de contraventions ou une erreur en cas de problème.

    - bash 'curl -i http://127.0.0.1:5000/infractions?etablissement=...'

    Returns:
        Response: JSON avec les contraventions ou un message d'erreur.
    """
    nom = request.args.get("etablissement", "").strip()
    if not nom:
        return jsonify({"erreur": "Paramètre 'etablissement' manquant"}), 400

    try:
        db = get_db()
        # on réutilise la méthode existante
        contraventions = db.rechercher_contraventions(etablissement=nom)
        return jsonify([dict(c) for c in contraventions]), 200
    except Exception as e:
        return jsonify({"erreur": str(e)}), 500


# C1 (un plus)
@app.route("/pire-etablissement", methods=["GET"])
def obtenir_pire_etablissement():
    """
    Récupère l'établissement avec le plus grand nombre de contraventions.

    Retourne l'établissement et le nombre de contraventions sous la forme :
    { "etablissement": "...", "nb": 123 }.
    Si aucune donnée n'est trouvée, renvoie une erreur 404.

    - bash 'curl -i http://127.0.0.1:5000/pire-etablissement'

    Returns:
        Response: JSON avec l'établissement et le nombre de contraventions,
                ou un message d'erreur.
    """
    try:
        db = get_db()
        ligne = db.pire_etablissement()
        if ligne:
            return jsonify({
                "etablissement": ligne["etablissement"],
                "nb": ligne["nb"]
            }), 200
        else:
            return jsonify({"erreur": "Aucune donnée disponible"}), 404
    except Exception as e:
        return jsonify({"erreur": str(e)}), 500


# C1
@app.route("/statistiques", methods=["GET"])
def obtenir_statistiques():
    """
    Récupère les statistiques des contraventions par établissement.

    Retourne un JSON avec, pour chaque établissement,
    le nombre de contraventions
    du plus élevé au plus faible.

    - bash 'curl -i http://127.0.0.1:5000/statistiques'
    Returns:
        Response: JSON avec les statistiques ou un message d'erreur.
    """
    try:
        db = get_db()
        lignes = db.statistiques_infractions()
        donnees = [
            {"etablissement": ligne["etablissement"], "nb": ligne["nb"]}
            for ligne in lignes
        ]
        return jsonify(donnees), 200
    except Exception as e:
        return jsonify({"erreur": str(e)}), 500


# C2
@app.route("/statistiques/xml", methods=["GET"])
def obtenir_statistiques_xml():
    """
    Récupère les statistiques des contraventions et les renvoie au format XML.

    Retourne un fichier XML avec les établissements
    et leur nombre de contraventions.

    - bash 'curl -i http://127.0.0.1:5000/statistiques/xml'

    Returns:
        Response: Réponse XML avec les statistiques ou un message d'erreur.
    """
    try:
        db = get_db()
        lignes = db.statistiques_infractions()

        racine_xml = xml.etree.ElementTree.Element("statistiques")
        for ligne in lignes:
            noeaud = xml.etree.ElementTree.SubElement(
                racine_xml, "etablissement", nb=str(ligne["nb"])
            )
            noeaud.text = ligne["etablissement"]

        xml_bytes = xml.etree.ElementTree.tostring(
            racine_xml, encoding="utf-8", xml_declaration=True
        )
        reponse = make_response(xml_bytes)
        reponse.headers["Content-Type"] = "application/xml; charset=utf-8"
        return reponse
    except Exception as e:
        return jsonify({"erreur": str(e)}), 500


# C3
@app.route("/statistiques/csv", methods=["GET"])
def obtenir_statistiques_csv():
    """
    Récupère les statistiques des contraventions et les renvoie au format CSV.

    Retourne un fichier CSV avec les établissements
    et leur nombre de contraventions.

    - bash 'curl -i http://127.0.0.1:5000/statistiques/csv'

    Returns:
        Response: Réponse CSV avec les statistiques ou un message d'erreur.
    """

    try:
        db = get_db()
        lignes = db.statistiques_infractions()

        tampon = io.StringIO()
        writer = csv.writer(tampon, delimiter=";")
        writer.writerow(["etablissement",
                         "nombre d'infractions connues"])
        for ligne in lignes:
            writer.writerow([ligne["etablissement"], ligne["nb"]])

        contenu_csv = tampon.getvalue().encode("utf-8")
        reponse = make_response(contenu_csv)
        reponse.headers["Content-Type"] = "text/csv; charset=utf-8"
        reponse.headers["Content-Disposition"] = (
            "attachment; filename=statistiques.csv")

        return reponse

    except Exception as e:
        return jsonify({"erreur": str(e)}), 500


# E1
chemin_fichier = os.path.join(
    os.path.dirname(__file__), "schemas", "utilisateur_schema.json"
)
with open(chemin_fichier, encoding="utf-8") as f:
    utilisateur_schema = json.load(f)


# E1
@app.route("/api/utilisateurs", methods=["POST"])
def creer_utilisateur_api():
    """
    Crée un nouvel utilisateur via une requête API.

    Cette fonction reçoit les données de l'utilisateur au format JSON,
    les valide selon un schéma prédéfini, puis crée un utilisateur
    dans la base de données avec un mot de passe haché.

    - bash 'curl -X POST http://127.0.0.1:5000/api/utilisateurs \
        -H "Content-Type: application/json" \
        -d '{"username":"adam-test","password":"MotDePasse123", \
        "nom":"test","prenom":"adam"}'

    Returns:
        Response: Un message de succès ou d'erreur en fonction du résultat.
    """
    try:
        donnees = request.get_json()
        validate(donnees, utilisateur_schema)

        salt = uuid.uuid4().hex
        password_hash = hashlib.sha512(
            str(donnees["password"] + salt).encode("utf-8")
        ).hexdigest()

        db = get_db()
        utilisateur_id = db.creer_utilisateur(
            username=donnees["username"],
            password_hash=password_hash,
            salt=salt,
            nom=donnees["nom"],
            prenom=donnees["prenom"],
            photo_profil=None
        )

        if utilisateur_id:
            return jsonify({"message": "Utilisateur créé avec succès"}), 201
        else:
            return jsonify({
                "message": "Erreur lors de la création de l'utilisateur"
            }), 500

    except ValidationError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# E2
@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    """
    Gère l'inscription d'un nouvel utilisateur.

    Cette fonction permet à un utilisateur de créer un compte en remplissant
    un formulaire. Elle vérifie la validité des informations saisies
    (nom, prénom, nom d'utilisateur, mot de passe) et crée
    un nouvel utilisateur dans la base de données.

    Returns:
        Response: La page HTML de l'inscription avec un message de succès
        ou d'erreur.
    """
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        prenom = request.form.get("prenom", "").strip()
        nom_utilisateur = request.form.get("nom_utilisateur", "").strip()
        mot_de_passe = request.form.get("mot_de_passe", "")

        # Vérifie si un champ est vide
        if not nom or not prenom or not nom_utilisateur or not mot_de_passe:
            return render_template(
                "inscription.html",
                message="Veuillez remplir tous les champs.",
                couleur="red"
            )

        # Vérifie la longueur du nom et prénom
        if len(nom) < 2 or len(prenom) < 2:
            return render_template(
                "inscription.html",
                message="""Le nom et le prénom doivent contenir
                au moins 2 caractères.""",
                couleur="red"
            )

        # Vérifie le nom d'utilisateur avec une expression régulière simple
        if not re.match(r"^[a-zA-Z0-9_.-]{3,20}$", nom_utilisateur):
            return render_template(
                "inscription.html",
                message="""Nom d'utilisateur invalide (3 à 20 caractères,
                lettres et chiffres uniquement).""",
                couleur="red"
            )

        # Vérifie la force du mot de passe :
        # au moins 8 caractères, une majuscule et un chiffre
        if not re.match(r"^(?=.*[A-Z])(?=.*\d).{8,}$", mot_de_passe):
            return render_template(
                "inscription.html",
                message="""Mot de passe trop faible. Il doit contenir
                une majuscule, un chiffre et au moins 8 caractères.""",
                couleur="red"
            )

        db = get_db()

        # Vérifie si le nom d'utilisateur est déjà dans la base
        if db.obtenir_utilisateur(nom_utilisateur):
            return render_template(
                "inscription.html",
                message="Ce nom d'utilisateur est déjà pris.",
                couleur="red"
            )

        # Hachage du mot de passe avec un salt
        salt = uuid.uuid4().hex
        mot_de_passe_hache = hashlib.sha512(
            (salt + mot_de_passe).encode()
        ).hexdigest()

        # Création de l'utilisateur
        utilisateur_id = db.creer_utilisateur(
            username=nom_utilisateur,
            password_hash=mot_de_passe_hache,
            salt=salt,
            nom=nom,
            prenom=prenom,
            photo_profil=None
        )

        if utilisateur_id:
            return render_template(
                "inscription.html",
                message="Compte créé avec succès.",
                couleur="green"
            )
        else:
            return render_template(
                "inscription.html",
                message="Une erreur est survenue lors de l'inscription.",
                couleur="red"
            )
    return render_template("inscription.html")


# E2
@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    """
    Gère la connexion des utilisateurs.

    Cette fonction permet à un utilisateur
    de se connecter en vérifiant son nom d'utilisateur
    et son mot de passe. Si les informations sont valides,
    une session est créée.

    Returns:
        Response: La page de connexion avec un message d'erreur
        ou une redirection vers la page d'accueil.
    """
    if request.method == "POST":
        nom_utilisateur = request.form.get("nom_utilisateur")
        mot_de_passe = request.form.get("mot_de_passe")

        db = get_db()
        utilisateur = db.obtenir_utilisateur(nom_utilisateur)

        if not utilisateur:
            message = "Nom d'utilisateur ou mot de passe incorrect."
            return render_template(
                "connexion.html",
                message=message,
                couleur="red"
            )

        mot_de_passe_hash = hashlib.sha512(
            (utilisateur["salt"] + mot_de_passe).encode()
        ).hexdigest()

        if mot_de_passe_hash == utilisateur["password_hash"]:
            session_id = str(uuid.uuid4())
            session["utilisateur"] = utilisateur["username"]
            session["id_session"] = session_id

            db.ajouter_session(session_id, utilisateur["username"])
            return redirect(url_for("accueil"))
        else:
            message = "Nom d'utilisateur ou mot de passe incorrect."
            return render_template(
                "connexion.html",
                message=message,
                couleur="red"
            )
    return render_template("connexion.html")


# E2
@app.route("/deconnexion")
def deconnexion():
    """
    Déconnecte l'utilisateur.

    Cette fonction supprime la session active
    et redirige l'utilisateur vers la page d'accueil
    après l'avoir informé qu'il a été déconnecté.

    Returns:
        Response: Redirection vers la page d'accueil
        avec un message flash de déconnexion.
    """
    db = get_db()

    identifiant_session = session.get("id_session")
    if identifiant_session:
        db.supprimer_session(identifiant_session)

    session.clear()
    flash("Vous avez été déconnecté.")
    return redirect(url_for("accueil"))


# E2
@app.route("/profil")
@connexion_requise
def profil():
    """
    Affiche le profil de l'utilisateur connecté.

    Cette fonction récupère les informations de l'utilisateur connecté
    et les affiche sur la page de profil. Si l'utilisateur n'est pas trouvé,
    il est redirigé vers la page de connexion.

    Returns:
        Response: La page de profil de l'utilisateur
        ou une redirection vers la page de connexion.
    """
    db = get_db()
    utilisateur = db.obtenir_utilisateur(session["utilisateur"])

    if not utilisateur:
        return redirect(url_for("connexion"))

    return render_template("profil.html", utilisateur=utilisateur)


# E2
@app.route("/photo/<nom_utilisateur>")
@connexion_requise
def photo_profil(nom_utilisateur):
    """
    Affiche la photo de profil de l'utilisateur.

    Cette fonction récupère l'image de profil de l'utilisateur spécifié
    par le nom d'utilisateur
    et la renvoie en tant qu'image JPEG. Si l'utilisateur
    n'a pas de photo de profil, une erreur 404 est renvoyée.

    Args:
        nom_utilisateur (str): Le nom d'utilisateur de l'utilisateur
        dont la photo doit être affichée.

    Returns:
        Response: L'image de profil au format JPEG
        ou une erreur 404 si aucune photo n'est trouvée.
    """
    db = get_db()
    utilisateur = db.obtenir_utilisateur(nom_utilisateur)

    if utilisateur and utilisateur["photo_profil"]:
        image = io.BytesIO(utilisateur["photo_profil"])
        return send_file(image, mimetype="image/jpeg")
    else:
        return "", 404


# E2
@app.route("/televerser-photo", methods=["POST"])
@connexion_requise
def televerser_photo():
    """
    Permet à l'utilisateur de téléverser une photo de profil.

    Cette fonction vérifie que le fichier téléversé
    est une image valide (.png, .jpg, .jpeg).
    Elle enregistre la photo dans la base de données
    et redirige l'utilisateur vers la page de profil
    avec un message de succès.

    Returns:
        Response: Redirection vers la page de profil
        avec un message de succès ou d'erreur.
    """
    photo = request.files.get("photo")

    if not photo:
        return redirect(url_for("profil"),
                        message="Aucun fichier téléversé",
                        couleur="red")

    if not photo.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        return redirect(url_for("profil"),
                        message="Fichier non autorisé",
                        couleur="red")

    contenu = photo.read()

    db = get_db()
    db.ajout_photo_profil(session["utilisateur"], contenu)

    return render_template(
        "profil.html",
        message="Photo de profil téléversée",
        couleur="green",
        utilisateur=db.obtenir_utilisateur(session["utilisateur"])
    )


# E2
@app.route("/rechercher-etablissements")
@connexion_requise
def rechercher_etablissements():
    """
    Recherche les établissements en fonction d'une entrée utilisateur.

    Cette fonction récupère un terme de recherche et renvoie les établissements
    correspondants, en limitant les résultats à 10. Les résultats sont renvoyés
    sous forme de JSON.

    Returns:
        Response: JSON avec les établissements
        correspondants ou une liste vide.
    """
    entree = request.args.get("entree", "").lower()
    db = get_db()
    curseur = db.connexion.cursor()
    curseur.execute("""
        SELECT DISTINCT id_poursuite, etablissement
        FROM contraventions
        WHERE LOWER(etablissement) LIKE ?
        LIMIT 10
    """, (f"%{entree}%",))

    resultats = [
        {"id": i["id_poursuite"], "nom": i["etablissement"]}
        for i in curseur.fetchall()]

    return jsonify(resultats)


# E2
@app.route("/etablissements-surveilles", methods=["GET", "POST"])
@connexion_requise
def etablissements_surveilles():
    """
    Permet à l'utilisateur de gérer ses établissements surveillés.

    Cette fonction affiche la liste des établissements surveillés
    et permet à l'utilisateur
    de mettre à jour cette liste en ajoutant de nouveaux établissements.

    Returns:
        Response: La page HTML des établissements surveillés
        avec un message de mise à jour ou un message d'erreur.
    """
    db = get_db()
    utilisateur = db.obtenir_utilisateur(session["utilisateur"])

    message = None

    if request.method == "POST":
        donnees = request.form.get("etablissements", "")
        db.ajout_etablissements_surveilles(session["utilisateur"], donnees)
        message = "Liste mise à jour."
        utilisateur = db.obtenir_utilisateur(session["utilisateur"])

    ids_etablissements = []
    noms = []

    if utilisateur and utilisateur["etablissements_surveilles"]:
        ids_etablissements = (
            utilisateur["etablissements_surveilles"].split(","))
        resultats = db.etablissements_par_ids(ids_etablissements)
        noms = [
            f"{i['id_poursuite']} - {i['etablissement']}"
            for i in resultats]

    return render_template(
        "etablissements_surveilles.html",
        utilisateur=utilisateur,
        etablissements_affiches=noms,
        etablissements_surveilles=(
            utilisateur["etablissements_surveilles"] or ""
        ),
        message=message,
        couleur="green"
    )


# E3
if __name__ == '__main__':
    """
    Démarre l'application Flask et configure
    la mise à jour quotidienne de la base de données.
    """
    maj_minuit()
    app.run(debug=True)
