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

-- 5. Table AVIS
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


-- 1. Ajouter les champs d'état et de validation à la table panier
ALTER TABLE public.panier 
ADD COLUMN etat TEXT DEFAULT 'en_cours' CHECK (etat IN ('en_cours', 'valide', 'annule')),
ADD COLUMN date_validation TIMESTAMPTZ;

-- 3. Commentaire pour expliquer la logique (Optionnel)
COMMENT ON COLUMN public.panier.etat IS 'en_cours = panier actif, valide = commande confirmée, annule = panier abandonné';



-- 1. Activer l'extension pgcrypto (nécessaire pour les fonctions de hachage)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 3. Réinsérer les utilisateurs avec mot de passe haché en SHA1
-- encode(digest('votre_texte', 'sha1'), 'hex') permet d'avoir le résultat en texte lisible
INSERT INTO public.utilisateur (nom, email, mot_de_passe) VALUES
(
  'Jean Dupont', 
  'jean.dupont@email.com', 
  encode(digest('password123', 'sha1'), 'hex')
),
(
  'Marie Louise', 
  'marie.louise@email.com', 
  encode(digest('secret456', 'sha1'), 'hex')
),
(
  'Lucas Bernard', 
  'lucas.b@email.com', 
  encode(digest('admin789', 'sha1'), 'hex')
);

-- 4. Vérification du rendu
SELECT id_utilisateur, nom, email, mot_de_passe FROM public.utilisateur;

-- 1. Insertion des PRODUITS
INSERT INTO public.produit (nom_produit, description, prix, stock) VALUES
('MacBook Air M2', 'Ordinateur portable ultra-fin Apple', 1199.00, 15),
('iPhone 15 Pro', 'Le dernier smartphone avec châssis titane', 1229.00, 25),
('AirPods Pro 2', 'Écouteurs avec réduction de bruit active', 279.00, 60),
('Magic Mouse', 'Souris sans fil rechargeable blanche', 85.00, 40),
('Station de charge', 'Chargeur 3-en-1 sans fil', 45.50, 100);

-- 3. Insertion des PANIERS (avec gestion de l'état commande)
-- Rappel : id_utilisateur 1=Jean, 2=Marie, 3=Lucas (suite au script précédent)
INSERT INTO public.panier (id_utilisateur, etat, date_validation) VALUES
(1, 'valide', NOW() - INTERVAL '3 days'), -- Commande passée de Jean
(1, 'en_cours', NULL),                    -- Panier actuel de Jean
(2, 'valide', NOW() - INTERVAL '1 day'),  -- Commande passée de Marie
(3, 'en_cours', NULL);                    -- Panier actuel de Lucas

-- 4. Insertion du CONTENU des paniers (Lien entre Paniers et Produits)
INSERT INTO public.contenu_panier (id_panier, id_produit, quantite) VALUES
(1, 1, 1), -- Panier 1 : 1 MacBook
(1, 4, 1), -- Panier 1 : 1 Mouse
(2, 3, 2), -- Panier 2 : 2 AirPods
(3, 2, 1), -- Panier 3 : 1 iPhone
(3, 5, 2), -- Panier 3 : 2 Stations de charge
(4, 3, 1); -- Panier 4 : 1 AirPods

-- 5. Insertion des AVIS (Lien entre Utilisateurs et Produits)
INSERT INTO public.avis (id_utilisateur, id_produit, note, commentaire) VALUES
(1, 1, 5, 'Le MacBook est incroyablement rapide et silencieux.'),
(1, 4, 3, 'Design sympa mais pas très ergonomique pour le prix.'),
(2, 2, 5, 'Photos magnifiques, l écran est superbe.'),
(3, 3, 4, 'Très bon son, mais glisse parfois des oreilles.');
