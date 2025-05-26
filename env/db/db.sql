CREATE TABLE contraventions (
    id_poursuite INTEGER PRIMARY KEY,
    business_id INTEGER,
    date DATE,
    description TEXT,
    adresse VARCHAR(255),
    date_jugement DATE,
    etablissement VARCHAR(255),
    montant INTEGER,
    proprietaire VARCHAR(255),
    ville VARCHAR(255),
    statut VARCHAR(255),
    date_statut DATE,
    categorie VARCHAR(255)
);


CREATE TABLE utilisateurs (
    id_utilisateur INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    photo_profil BLOB
);


CREATE TABLE sessions (
    id_session TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    FOREIGN KEY(username) REFERENCES utilisateurs(username)
        ON DELETE CASCADE
);
