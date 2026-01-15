import os
from typing import Dict, Any, Optional
import json
from anthropic import Anthropic

# Configuration Anthropic Claude
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def parse_user_intent(user_query: str) -> Dict[str, Any]:
    """
    Analyse l'intention de l'utilisateur et structure la requête
    
    Args:
        user_query: La requête en langage naturel de l'utilisateur
        
    Returns:
        Dict contenant l'intent structuré
    """
    
    system_prompt = """Tu es un assistant qui analyse les requêtes utilisateur pour interagir avec une base de données MongoDB contenant des événements Polymarket.

La collection "cleaned" contient des événements avec ces champs:
- _id (ObjectId): ID MongoDB
- id (string): ID unique (UUID)
- title (string): Titre de l'événement
- category (string): Catégorie (Sports, Crypto, Pop-Culture)
- description (string): Description
- commentCount (int): Nombre de commentaires
- volume (float): Volume de trading
- ticker (string): Symbole
- slug (string): Slug unique
- startDate, endDate, closedTime: Dates
- image, icon: URLs
- resolutionSource, seriesSlug: Métadonnées

Actions disponibles:
1. RECHERCHER (READ) - Rechercher/lister des événements
2. CREER (CREATE) - Créer un nouvel événement
3. MODIFIER (UPDATE) - Mettre à jour un événement existant
4. SUPPRIMER (DELETE) - Supprimer un événement
5. STATISTIQUES (STATS) - Obtenir des statistiques

Analyse la requête et retourne un JSON avec:
{
  "action": "RECHERCHER|CREER|MODIFIER|SUPPRIMER|STATISTIQUES",
  "confidence": 0.0-1.0,
  "parameters": {
    // Paramètres spécifiques à l'action
    // Pour RECHERCHER: {"search": "...", "category": "...", "limit": ...}
    // Pour CREER: {"title": "...", "category": "...", "description": "...", ...}
    // Pour MODIFIER: {"event_id": "...", "updates": {...}}
    // Pour SUPPRIMER: {"event_id": "..." ou "search": "..."}
    // Pour STATISTIQUES: {"type": "general|category|volume"}
  },
  "summary": {
    "what": "Description claire de ce qui va être fait",
    "where": "Sur quels événements/données (précis)",
    "impact": "Quel sera l'impact (lecture seule, création, modification, suppression)"
  },
  "needs_clarification": false,
  "clarification_questions": []
}

Si la requête est ambiguë, mets needs_clarification à true et fournis des questions de clarification."""

    try:
        # Vérifier que la clé API est présente
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY non trouvée dans les variables d'environnement")
        
        print(f"🔍 Analyse de la requête: {user_query}")
        
        # Ajouter instruction JSON dans le prompt système
        full_prompt = system_prompt + "\n\nRéponds UNIQUEMENT avec un objet JSON valide, sans texte avant ou après."
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            temperature=0.3,
            system=full_prompt,
            messages=[
                {"role": "user", "content": user_query}
            ]
        )
        
        # Extraire le texte de la réponse
        response_text = response.content[0].text
        print(f"📝 Réponse brute de Claude:\n{response_text}")
        
        # Nettoyer la réponse si elle contient des balises markdown
        if response_text.strip().startswith("```"):
            # Retirer les balises ```json ... ```
            lines = response_text.strip().split("\n")
            response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
        
        intent = json.loads(response_text)
        print(f"✅ Intent parsé avec succès")
        return intent
        
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {str(e)}")
        print(f"📄 Texte reçu: {response_text if 'response_text' in locals() else 'N/A'}")
        return {
            "action": "ERROR",
            "confidence": 0.0,
            "parameters": {},
            "summary": {
                "what": "Erreur de format de réponse",
                "where": "N/A",
                "impact": f"La réponse de l'IA n'est pas au format JSON valide"
            },
            "needs_clarification": True,
            "clarification_questions": [f"Erreur technique: {str(e)}. Veuillez réessayer."]
        }
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "action": "ERROR",
            "confidence": 0.0,
            "parameters": {},
            "summary": {
                "what": "Erreur lors de l'analyse",
                "where": "N/A",
                "impact": f"Erreur: {str(e)}"
            },
            "needs_clarification": True,
            "clarification_questions": [f"Erreur technique: {str(e)}. Veuillez réessayer."]
        }


def execute_intent(intent: Dict[str, Any], api_base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """
    Exécute l'intent analysé en appelant l'API appropriée
    
    Args:
        intent: L'intent structuré
        api_base_url: URL de base de l'API
        
    Returns:
        Résultat de l'exécution
    """
    import requests
    
    action = intent.get("action")
    params = intent.get("parameters", {})
    
    try:
        if action == "RECHERCHER":
            # GET /events avec filtres
            search_params = {
                "page": 1,
                "per_page": params.get("limit", 10)
            }
            if params.get("search"):
                search_params["search"] = params["search"]
            if params.get("category"):
                search_params["category"] = params["category"]
            
            response = requests.get(f"{api_base_url}/events", params=search_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "action": "RECHERCHER",
                "data": data,
                "message": f"Trouvé {data.get('total_count', 0)} événement(s)"
            }
        
        elif action == "CREER":
            # POST /events
            response = requests.post(f"{api_base_url}/events", json=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "action": "CREER",
                "data": data,
                "message": "Événement créé avec succès"
            }
        
        elif action == "MODIFIER":
            # PUT /events/{id}
            event_id = params.get("event_id")
            updates = params.get("updates", {})
            
            if not event_id:
                return {
                    "success": False,
                    "action": "MODIFIER",
                    "data": None,
                    "message": "ID d'événement manquant"
                }
            
            response = requests.put(f"{api_base_url}/events/{event_id}", json=updates, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "action": "MODIFIER",
                "data": data,
                "message": "Événement modifié avec succès"
            }
        
        elif action == "SUPPRIMER":
            # DELETE /events/{id}
            event_id = params.get("event_id")
            
            if not event_id:
                # Si pas d'ID, chercher d'abord l'événement
                search = params.get("search")
                if search:
                    response = requests.get(f"{api_base_url}/events", params={"search": search, "per_page": 1}, timeout=10)
                    response.raise_for_status()
                    events = response.json().get("data", [])
                    if events:
                        event_id = events[0].get("_id")
                    else:
                        return {
                            "success": False,
                            "action": "SUPPRIMER",
                            "data": None,
                            "message": "Événement non trouvé"
                        }
            
            response = requests.delete(f"{api_base_url}/events/{event_id}", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "action": "SUPPRIMER",
                "data": data,
                "message": "Événement supprimé avec succès"
            }
        
        elif action == "STATISTIQUES":
            # GET /stats ou /categories
            stat_type = params.get("type", "general")
            
            if stat_type == "category":
                response = requests.get(f"{api_base_url}/categories", timeout=10)
            else:
                response = requests.get(f"{api_base_url}/stats", timeout=10)
            
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "action": "STATISTIQUES",
                "data": data,
                "message": "Statistiques récupérées"
            }
        
        else:
            return {
                "success": False,
                "action": action,
                "data": None,
                "message": f"Action non reconnue: {action}"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "action": action,
            "data": None,
            "message": f"Erreur API: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "action": action,
            "data": None,
            "message": f"Erreur: {str(e)}"
        }


def generate_natural_response(intent: Dict[str, Any], result: Dict[str, Any]) -> str:
    """
    Génère une réponse en langage naturel basée sur le résultat
    
    Args:
        intent: L'intent d'origine
        result: Le résultat de l'exécution
        
    Returns:
        Réponse en langage naturel
    """
    
    if not result.get("success"):
        return f"❌ {result.get('message', 'Une erreur est survenue')}"
    
    action = result.get("action")
    data = result.get("data", {})
    
    if action == "RECHERCHER":
        count = data.get("total_count", 0)
        if count == 0:
            return "🔍 Aucun événement trouvé correspondant à votre recherche."
        elif count == 1:
            return f"✅ J'ai trouvé 1 événement correspondant à votre recherche."
        else:
            return f"✅ J'ai trouvé {count} événements correspondant à votre recherche."
    
    elif action == "CREER":
        event_id = data.get("data", {}).get("id", "N/A")
        return f"✅ Événement créé avec succès! ID: {event_id}"
    
    elif action == "MODIFIER":
        return "✅ Événement modifié avec succès!"
    
    elif action == "SUPPRIMER":
        return "✅ Événement supprimé avec succès!"
    
    elif action == "STATISTIQUES":
        total = data.get("total_events", 0)
        categories = len(data.get("categories", []))
        return f"📊 La collection contient {total} événements répartis en {categories} catégories."
    
    return "✅ Opération réussie!"
