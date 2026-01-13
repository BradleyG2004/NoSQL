-- Dans Supabase, on ne crée pas la base, on crée les tables directement 
-- dans le schéma public.

-- 1. Table UTILISATEUR
CREATE TABLE IF NOT EXISTS public.utilisateur (
    id_utilisateur SERIAL PRIMARY KEY,
    nom TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    mot_de_passe TEXT NOT NULL,
    date_inscription TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Table PRODUIT
CREATE TABLE IF NOT EXISTS public.produit (
    id_produit SERIAL PRIMARY KEY,
    nom_produit TEXT NOT NULL,
    description TEXT,
    prix DECIMAL(10, 2) NOT NULL,
    stock INT DEFAULT 0
);

-- 3. Table PANIER
CREATE TABLE IF NOT EXISTS public.panier (
    id_panier SERIAL PRIMARY KEY,
    id_utilisateur INT NOT NULL,
    date_creation TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_panier_utilisateur FOREIGN KEY (id_utilisateur) 
        REFERENCES public.utilisateur(id_utilisateur) ON DELETE CASCADE
);

-- 4. Table de liaison CONTENU_PANIER
CREATE TABLE IF NOT EXISTS public.contenu_panier (
    id_panier INT NOT NULL,
    id_produit INT NOT NULL,
    quantite INT DEFAULT 1 CHECK (quantite > 0),
    PRIMARY KEY (id_panier, id_produit),
    CONSTRAINT fk_cp_panier FOREIGN KEY (id_panier) 
        REFERENCES public.panier(id_panier) ON DELETE CASCADE,
    CONSTRAINT fk_cp_produit FOREIGN KEY (id_produit) 
        REFERENCES public.produit(id_produit)
);

-- 5. Table COMMANDE (Relation 1:1 avec Panier)
CREATE TABLE IF NOT EXISTS public.commande (
    id_commande SERIAL PRIMARY KEY,
    id_panier INT UNIQUE NOT NULL, 
    date_commande TIMESTAMPTZ DEFAULT NOW(),
    statut_paiement TEXT DEFAULT 'En attente',
    CONSTRAINT fk_commande_panier FOREIGN KEY (id_panier) 
        REFERENCES public.panier(id_panier)
);

-- 6. Table AVIS
CREATE TABLE IF NOT EXISTS public.avis (
    id_avis SERIAL PRIMARY KEY,
    id_utilisateur INT NOT NULL,
    id_produit INT NOT NULL,
    note INT CHECK (note >= 1 AND note <= 5),
    commentaire TEXT,
    date_publication TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_avis_utilisateur FOREIGN KEY (id_utilisateur) 
        REFERENCES public.utilisateur(id_utilisateur),
    CONSTRAINT fk_avis_produit FOREIGN KEY (id_produit) 
        REFERENCES public.produit(id_produit)
);

-- 1. Supprimer la table commande qui n'est plus nécessaire
DROP TABLE IF EXISTS public.commande;

-- 2. Ajouter les champs d'état et de validation à la table panier
ALTER TABLE public.panier 
ADD COLUMN etat TEXT DEFAULT 'en_cours' CHECK (etat IN ('en_cours', 'valide', 'annule')),
ADD COLUMN date_validation TIMESTAMPTZ;

-- 3. Commentaire pour expliquer la logique (Optionnel)
COMMENT ON COLUMN public.panier.etat IS 'en_cours = panier actif, valide = commande confirmée, annule = panier abandonné';