# Assistant IA pour Polymarket Dashboard

## 🤖 Fonctionnalité

L'Assistant IA permet aux utilisateurs d'interagir avec la collection MongoDB en utilisant du **langage naturel**.

## 🔄 Processus

```
┌─────────────┐
│   USER      │  Tape: "Montre-moi les événements Sports"
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────┐
│  STREAMLIT (streamlit_app.py)                  │
│  - Capture la requête en langage naturel       │
│  - Affiche l'interface utilisateur              │
└──────┬──────────────────────────────────────────┘
       │
       │ parse_user_intent(user_query)
       ▼
┌─────────────────────────────────────────────────┐
│  AI ASSISTANT (ai_assistant.py)                 │
│  ┌────────────────────────────────────────┐    │
│  │ Claude 3.5 Sonnet (Anthropic)          │    │
│  │ - Analyse l'intention                   │    │
│  │ - Extrait les paramètres                │    │
│  │ - Calcule la confiance                  │    │
│  │ - Génère le résumé WHAT/WHERE/IMPACT   │    │
│  └────────────────────────────────────────┘    │
└──────┬──────────────────────────────────────────┘
       │
       │ Retourne intent structuré:
       │ {action, confidence, parameters, summary, ...}
       ▼
┌─────────────────────────────────────────────────┐
│  STREAMLIT - Confirmation                       │
│  ┌──────────────────────────────────────┐      │
│  │ 🎯 QUOI: Rechercher des événements   │      │
│  │ 📍 OÙ: Catégorie Sports              │      │
│  │ 📖 IMPACT: Lecture seule              │      │
│  └──────────────────────────────────────┘      │
│  [✅ Confirmer]  [❌ Annuler]  [🔄 Modifier]   │
└──────┬──────────────────────────────────────────┘
       │
       │ Si USER clique "✅ Confirmer"
       │ execute_intent(intent)
       ▼
┌─────────────────────────────────────────────────┐
│  AI ASSISTANT - Exécution                       │
│  - Construit la requête HTTP appropriée        │
│  - Appelle l'API FastAPI                       │
└──────┬──────────────────────────────────────────┘
       │
       │ HTTP Request (GET/POST/PUT/DELETE)
       ▼
┌─────────────────────────────────────────────────┐
│  FASTAPI API (main.py)                          │
│  - Reçoit la requête                            │
│  - Valide les données (Pydantic)               │
│  - Execute l'opération CRUD                     │
└──────┬──────────────────────────────────────────┘
       │
       │ Query/Insert/Update/Delete
       ▼
┌─────────────────────────────────────────────────┐
│  MONGODB (Collection "cleaned")                 │
│  - Exécute l'opération                          │
│  - Retourne les résultats                       │
└──────┬──────────────────────────────────────────┘
       │
       │ Données JSON
       ▼
┌─────────────────────────────────────────────────┐
│  AI ASSISTANT - Réponse                         │
│  generate_natural_response(intent, result)      │
│  - Génère une réponse en français naturel      │
└──────┬──────────────────────────────────────────┘
       │
       │ "✅ J'ai trouvé 15 événements Sports"
       ▼
┌─────────────────────────────────────────────────┐
│  STREAMLIT - Affichage                          │
│  - Message de succès/erreur                     │
│  - DataFrame avec les résultats                 │
│  - Graphiques si pertinent                      │
└──────┬──────────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│   USER      │  Voit les résultats
└─────────────┘

```

## ⚙️ Configuration

### 1. Obtenir une clé API Anthropic

1. Créez un compte sur https://console.anthropic.com
2. Allez dans **API Keys**
3. Cliquez sur **Create Key**
4. Copiez la clé

### 2. Ajouter la clé dans `.env`

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
MONGO_URI=mongodb+srv://...
DB2=polymarket_db
```

### 3. Installer les dépendances

```bash
pip install anthropic
```

## 🎯 Actions Supportées

### 1. RECHERCHER (READ)
**Exemples :**
- *"Montre-moi tous les événements Sports"*
- *"Trouve les événements avec plus de 100 commentaires"*
- *"Liste les événements Crypto"*

### 2. STATISTIQUES (STATS)
**Exemples :**
- *"Donne-moi les statistiques"*
- *"Combien d'événements avons-nous ?"*
- *"Quelle est la répartition par catégorie ?"*

### 3. CRÉER (CREATE)
**Exemples :**
- *"Crée un événement Sports intitulé 'Super Bowl 2026'"*
- *"Ajoute un nouvel événement Crypto"*

### 4. MODIFIER (UPDATE)
**Exemples :**
- *"Change le titre de l'événement X"*
- *"Mets à jour le nombre de commentaires"*

### 5. SUPPRIMER (DELETE)
**Exemples :**
- *"Supprime l'événement X"*
- *"Efface tous les événements avec 0 commentaires"*

## 🧠 Intelligence

L'assistant utilise **Claude 3.5 Sonnet** (Anthropic) pour :

1. **Analyser l'intention** : Comprendre ce que veut l'utilisateur
2. **Extraire les paramètres** : Identifier les filtres, valeurs, etc.
3. **Évaluer la confiance** : Score de 0-100%
4. **Générer un résumé** : QUOI / OÙ / IMPACT
5. **Détecter les ambiguïtés** : Demander des clarifications si nécessaire

## 📋 Format de l'Intent

```json
{
  "action": "RECHERCHER|CREER|MODIFIER|SUPPRIMER|STATISTIQUES",
  "confidence": 0.85,
  "parameters": {
    "category": "Sports",
    "search": "Super Bowl"
  },
  "summary": {
    "what": "Rechercher des événements",
    "where": "Dans la catégorie Sports contenant 'Super Bowl'",
    "impact": "Lecture seule - Aucune modification"
  },
  "needs_clarification": false,
  "clarification_questions": []
}
```

## 🔒 Sécurité

- ✅ **Confirmation obligatoire** avant toute action
- ✅ **Résumé clair** de l'impact (lecture/écriture/suppression)
- ✅ **Annulation possible** à tout moment
- ✅ **Validation** des paramètres côté API

## 💡 Conseils d'Utilisation

1. **Soyez précis** : Plus votre requête est claire, meilleure sera l'analyse
2. **Vérifiez le résumé** : Lisez attentivement QUOI/OÙ/IMPACT avant de confirmer
3. **Utilisez des exemples** : Inspirez-vous des exemples fournis
4. **Confiance < 70%** : Reformulez si la confiance est faible

## 🚀 Lancement

```bash
# Terminal 1 - API FastAPI
cd TP2/API
uvicorn main:app --reload --port 8000

# Terminal 2 - Streamlit
cd TP2/API
streamlit run streamlit_app.py
```

Puis allez sur la page **🤖 Assistant IA** !
