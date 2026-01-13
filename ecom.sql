-- Initialisation de la base de données
CREATE DATABASE IF NOT EXISTS boutique_gcp;
USE boutique_gcp;

-- 1. Table UTILISATEUR
CREATE TABLE UTILISATEUR (
    id_utilisateur INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Table PRODUIT
CREATE TABLE PRODUIT (
    id_produit INT PRIMARY KEY AUTO_INCREMENT,
    nom_produit VARCHAR(200) NOT NULL,
    description TEXT,
    prix DECIMAL(10, 2) NOT NULL,
    stock INT DEFAULT 0
) ENGINE=InnoDB;

-- 3. Table PANIER
CREATE TABLE PANIER (
    id_panier INT PRIMARY KEY AUTO_INCREMENT,
    id_utilisateur INT NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_panier_utilisateur FOREIGN KEY (id_utilisateur) 
        REFERENCES UTILISATEUR(id_utilisateur) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. Table de liaison CONTENU_PANIER (Relation N:N)
CREATE TABLE CONTENU_PANIER (
    id_panier INT NOT NULL,
    id_produit INT NOT NULL,
    quantite INT DEFAULT 1,
    PRIMARY KEY (id_panier, id_produit),
    CONSTRAINT fk_cp_panier FOREIGN KEY (id_panier) 
        REFERENCES PANIER(id_panier) ON DELETE CASCADE,
    CONSTRAINT fk_cp_produit FOREIGN KEY (id_produit) 
        REFERENCES PRODUIT(id_produit)
) ENGINE=InnoDB;

-- 5. Table COMMANDE (Relation 1:1 avec Panier)
CREATE TABLE COMMANDE (
    id_commande INT PRIMARY KEY AUTO_INCREMENT,
    id_panier INT UNIQUE NOT NULL, -- Le UNIQUE garantit le 1:1
    date_commande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut_paiement VARCHAR(50) DEFAULT 'En attente',
    CONSTRAINT fk_commande_panier FOREIGN KEY (id_panier) 
        REFERENCES PANIER(id_panier)
) ENGINE=InnoDB;

-- 6. Table AVIS
CREATE TABLE AVIS (
    id_avis INT PRIMARY KEY AUTO_INCREMENT,
    id_utilisateur INT NOT NULL,
    id_produit INT NOT NULL,
    note INT CHECK (note >= 1 AND note <= 5),
    commentaire TEXT,
    date_publication TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_avis_utilisateur FOREIGN KEY (id_utilisateur) 
        REFERENCES UTILISATEUR(id_utilisateur),
    CONSTRAINT fk_avis_produit FOREIGN KEY (id_produit) 
        REFERENCES PRODUIT(id_produit)
) ENGINE=InnoDB;