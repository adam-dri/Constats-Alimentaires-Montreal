import fonctionnalites

# A1 – Point d'entrée pour initialiser la BD via la fonctionnalité A1

if __name__ == '__main__':
    print("Initialisation de la base de données")
    try:
        fonctionnalites.A1()
        print("Téléchargement réussie.")
    except Exception as e:
        print("Une erreur est survenue lors de l'importation : ", e)
