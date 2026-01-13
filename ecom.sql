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


-- 1. Insérer des UTILISATEURS
INSERT INTO public.utilisateur (nom, email, mot_de_passe) VALUES
('Jean Dupont', 'jean.dupont@email.com', 'hash_password_123'),
('Marie Louise', 'marie.louise@email.com', 'hash_password_456'),
('Lucas Bernard', 'lucas.b@email.com', 'hash_password_789');

-- 2. Insérer des PRODUITS
INSERT INTO public.produit (nom_produit, description, prix, stock) VALUES
('Smartphone X', 'Dernier cri avec écran OLED', 899.99, 50),
('Casque Audio', 'Réduction de bruit active', 199.50, 100),
('Clavier Mécanique', 'Rétroéclairage RGB, Switchs rouges', 120.00, 30),
('Souris Gamer', 'Capteur haute précision 25k DPI', 75.00, 80);

-- 3. Créer des PANIERS (Certains 'en_cours', d'autres 'valide')
INSERT INTO public.panier (id_utilisateur, etat, date_validation) VALUES
(1, 'valide', NOW() - INTERVAL '2 days'), -- Une commande passée il y a 2 jours
(1, 'en_cours', NULL),                    -- Un panier actuel pour Jean
(2, 'valide', NOW() - INTERVAL '1 hour'),   -- Une commande récente de Marie
(3, 'en_cours', NULL);                    -- Un panier actuel pour Lucas

-- 4. Remplir les CONTENUS des paniers
INSERT INTO public.contenu_panier (id_panier, id_produit, quantite) VALUES
(1, 1, 1), -- Panier 1 (Valide) : 1 Smartphone
(1, 4, 1), -- Panier 1 (Valide) : 1 Souris
(2, 2, 2), -- Panier 2 (En cours) : 2 Casques
(3, 1, 1), -- Panier 3 (Valide) : 1 Smartphone
(4, 3, 1); -- Panier 4 (En cours) : 1 Clavier

-- 5. Ajouter des AVIS
INSERT INTO public.avis (id_utilisateur, id_produit, note, commentaire) VALUES
(1, 1, 5, 'Excellent téléphone, très rapide !'),
(1, 4, 4, 'Bonne souris mais un peu légère.'),
(2, 1, 3, 'Trop cher pour ce que c''est.');
