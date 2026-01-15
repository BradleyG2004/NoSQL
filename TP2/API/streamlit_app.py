import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Configuration de la page
st.set_page_config(
    page_title="Polymarket Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL de l'API
API_BASE_URL = "http://localhost:8000"

# Styles CSS personnalisés
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .success-msg {
        padding: 1rem;
        background-color: #d4edda;
        color: #155724;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-msg {
        padding: 1rem;
        background-color: #f8d7da;
        color: #721c24;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Fonctions pour interagir avec l'API
@st.cache_data(ttl=30)
def fetch_events(page=1, per_page=10, category=None, search=None):
    """Récupère les événements depuis l'API"""
    params = {"page": page, "per_page": per_page}
    if category and category != "Toutes":
        params["category"] = category
    if search:
        params["search"] = search
    
    try:
        response = requests.get(f"{API_BASE_URL}/events", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur lors de la récupération des événements: {e}")
        return None

@st.cache_data(ttl=30)
def fetch_statistics():
    """Récupère les statistiques depuis l'API"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur lors de la récupération des statistiques: {e}")
        return None

@st.cache_data(ttl=60)
def fetch_categories():
    """Récupère les catégories depuis l'API"""
    try:
        response = requests.get(f"{API_BASE_URL}/categories", timeout=10)
        response.raise_for_status()
        return response.json().get("categories", [])
    except Exception as e:
        st.error(f"Erreur lors de la récupération des catégories: {e}")
        return []

def create_event(event_data):
    """Crée un nouvel événement"""
    try:
        response = requests.post(f"{API_BASE_URL}/events", json=event_data, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur lors de la création: {e}")
        return None

def update_event(event_id, update_data):
    """Met à jour un événement"""
    try:
        response = requests.put(f"{API_BASE_URL}/events/{event_id}", json=update_data, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur lors de la mise à jour: {e}")
        return None

def delete_event(event_id):
    """Supprime un événement"""
    try:
        response = requests.delete(f"{API_BASE_URL}/events/{event_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur lors de la suppression: {e}")
        return None

# En-tête principal
st.markdown('<p class="main-header">📊 Polymarket Events Dashboard</p>', unsafe_allow_html=True)

# Sidebar pour la navigation
st.sidebar.title("🎯 Navigation")
page = st.sidebar.radio("Choisir une page:", ["📈 Dashboard", "📋 Gestion des Événements", "➕ Créer un Événement", "🤖 Assistant IA"])

# Refresh automatique
auto_refresh = st.sidebar.checkbox("🔄 Rafraîchissement automatique (30s)", value=False)
if auto_refresh:
    st.sidebar.info("Rafraîchissement actif...")

# ============================================================================
# PAGE: DASHBOARD
# ============================================================================
if page == "📈 Dashboard":
    st.title("📈 Tableau de Bord")
    
    # Récupérer les statistiques
    stats = fetch_statistics()
    
    if stats:
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Événements", stats.get("total_events", 0))
        
        with col2:
            categories_count = len(stats.get("categories", []))
            st.metric("🏷️ Catégories", categories_count)
        
        with col3:
            vol_stats = stats.get("volume_statistics", {})
            if vol_stats:
                avg_volume = vol_stats.get("avg_volume", 0)
                st.metric("💰 Volume Moyen", f"${avg_volume:,.2f}")
        
        with col4:
            if vol_stats:
                total_volume = vol_stats.get("total_volume", 0)
                st.metric("💵 Volume Total", f"${total_volume:,.0f}")
        
        st.divider()
        
        # Graphiques
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("📊 Distribution par Catégorie")
            categories = stats.get("categories", [])
            if categories:
                df_cat = pd.DataFrame(categories)
                df_cat.columns = ["Catégorie", "Nombre"]
                
                fig_pie = px.pie(
                    df_cat,
                    values="Nombre",
                    names="Catégorie",
                    title="Répartition des Événements",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_right:
            st.subheader("📈 Événements par Catégorie")
            if categories:
                fig_bar = px.bar(
                    df_cat,
                    x="Catégorie",
                    y="Nombre",
                    title="Nombre d'Événements par Catégorie",
                    color="Catégorie",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_bar.update_layout(showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
        
        # Statistiques de volume
        if vol_stats:
            st.subheader("💰 Statistiques de Volume")
            vol_col1, vol_col2, vol_col3, vol_col4 = st.columns(4)
            
            with vol_col1:
                st.info(f"**Min:** ${vol_stats.get('min_volume', 0):,.2f}")
            with vol_col2:
                st.info(f"**Moy:** ${vol_stats.get('avg_volume', 0):,.2f}")
            with vol_col3:
                st.info(f"**Max:** ${vol_stats.get('max_volume', 0):,.2f}")
            with vol_col4:
                st.info(f"**Total:** ${vol_stats.get('total_volume', 0):,.0f}")

# ============================================================================
# PAGE: GESTION DES ÉVÉNEMENTS
# ============================================================================
elif page == "📋 Gestion des Événements":
    st.title("📋 Gestion des Événements")
    
    # Filtres
    col_filter1, col_filter2, col_filter3 = st.columns([2, 2, 1])
    
    with col_filter1:
        categories = ["Toutes"] + fetch_categories()
        selected_category = st.selectbox("🏷️ Filtrer par catégorie:", categories)
    
    with col_filter2:
        search_query = st.text_input("🔍 Rechercher:", placeholder="Titre ou description...")
    
    with col_filter3:
        per_page = st.number_input("📄 Par page:", min_value=5, max_value=100, value=10, step=5)
    
    # Pagination
    page_number = st.number_input("📑 Page:", min_value=1, value=1, step=1)
    
    # Récupérer les événements
    events_data = fetch_events(
        page=page_number,
        per_page=per_page,
        category=selected_category if selected_category != "Toutes" else None,
        search=search_query if search_query else None
    )
    
    if events_data:
        # Informations de pagination
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.info(f"📄 Page {events_data['page']} sur {events_data['total_pages']}")
        with col_info2:
            st.info(f"📊 Total: {events_data['total_count']} événements")
        with col_info3:
            nav_text = ""
            if events_data['has_prev']:
                nav_text += "⬅️ Précédent  "
            if events_data['has_next']:
                nav_text += "➡️ Suivant"
            if nav_text:
                st.info(nav_text)
        
        # Convertir en DataFrame
        events = events_data.get("data", [])
        if events:
            df = pd.DataFrame(events)
            
            # Sélectionner les colonnes à afficher
            display_columns = ["_id", "title", "category", "commentCount", "volume", "ticker"]
            display_columns = [col for col in display_columns if col in df.columns]
            
            st.subheader(f"📊 {len(events)} événements affichés")
            
            # Afficher le dataframe avec formatage
            st.dataframe(
                df[display_columns],
                use_container_width=True,
                height=400,
                column_config={
                    "_id": st.column_config.TextColumn("ID MongoDB", width="small"),
                    "title": st.column_config.TextColumn("Titre", width="large"),
                    "category": st.column_config.TextColumn("Catégorie", width="small"),
                    "commentCount": st.column_config.NumberColumn("Commentaires", format="%d"),
                    "volume": st.column_config.NumberColumn("Volume", format="$%.2f"),
                    "ticker": st.column_config.TextColumn("Ticker", width="small")
                }
            )
            
            # Section de mise à jour/suppression
            st.divider()
            st.subheader("🔧 Actions sur les Événements")
            
            event_ids = df["_id"].tolist() if "_id" in df.columns else []
            event_titles = df["title"].tolist() if "title" in df.columns else []
            event_options = [f"{title} ({id})" for title, id in zip(event_titles, event_ids)]
            
            action_col1, action_col2 = st.columns(2)
            
            with action_col1:
                st.markdown("### ✏️ Mettre à jour un événement")
                if event_options:
                    selected_event = st.selectbox("Choisir un événement:", event_options)
                    selected_id = selected_event.split("(")[-1].strip(")")
                    
                    with st.form("update_form"):
                        new_title = st.text_input("Nouveau titre (optionnel):")
                        new_category = st.selectbox("Nouvelle catégorie (optionnel):", ["", "Sports", "Crypto", "Pop-Culture"])
                        new_comment_count = st.number_input("Nombre de commentaires (optionnel):", min_value=0, value=0)
                        
                        submit_update = st.form_submit_button("✏️ Mettre à jour")
                        
                        if submit_update:
                            update_data = {}
                            if new_title:
                                update_data["title"] = new_title
                            if new_category:
                                update_data["category"] = new_category
                            if new_comment_count > 0:
                                update_data["commentCount"] = new_comment_count
                            
                            if update_data:
                                result = update_event(selected_id, update_data)
                                if result and result.get("success"):
                                    st.success("✅ Événement mis à jour avec succès!")
                                    st.cache_data.clear()
                                    time.sleep(1)
                                    st.rerun()
                            else:
                                st.warning("⚠️ Aucune modification à appliquer")
            
            with action_col2:
                st.markdown("### 🗑️ Supprimer un événement")
                if event_options:
                    delete_event_selected = st.selectbox("Choisir un événement à supprimer:", event_options, key="delete_select")
                    delete_id = delete_event_selected.split("(")[-1].strip(")")
                    
                    if st.button("🗑️ Supprimer", type="primary"):
                        result = delete_event(delete_id)
                        if result and result.get("success"):
                            st.success("✅ Événement supprimé avec succès!")
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()
        else:
            st.warning("⚠️ Aucun événement trouvé")

# ============================================================================
# PAGE: CRÉER UN ÉVÉNEMENT
# ============================================================================
elif page == "➕ Créer un Événement":
    st.title("➕ Créer un Nouvel Événement")
    
    with st.form("create_event_form"):
        st.markdown("### 📝 Informations de l'Événement")
        
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("*Titre:", placeholder="Ex: Super Bowl 2026")
            category = st.selectbox("*Catégorie:", ["Sports", "Crypto", "Pop-Culture"])
            ticker = st.text_input("*Ticker:", placeholder="Ex: SPORT2026")
            slug = st.text_input("*Slug:", placeholder="Ex: super-bowl-2026")
            
        with col2:
            description = st.text_area("*Description:", placeholder="Description de l'événement...")
            comment_count = st.number_input("Nombre de commentaires:", min_value=0, value=0)
            volume = st.number_input("Volume:", min_value=0.0, value=0.0, step=1000.0)
        
        st.markdown("### 📅 Dates")
        col_date1, col_date2, col_date3 = st.columns(3)
        
        with col_date1:
            start_date = st.date_input("Date de début:")
            creation_date = st.date_input("Date de création:")
        
        with col_date2:
            end_date = st.date_input("Date de fin:")
        
        with col_date3:
            closed_time = st.date_input("Date de clôture:")
        
        st.markdown("### 🔗 Liens")
        col_link1, col_link2 = st.columns(2)
        
        with col_link1:
            image = st.text_input("*URL de l'image:", placeholder="https://example.com/image.png")
            icon = st.text_input("*URL de l'icône:", placeholder="https://example.com/icon.png")
        
        with col_link2:
            resolution_source = st.text_input("*Source de résolution:", placeholder="Official Source")
            series_slug = st.text_input("*Slug de série:", placeholder="series-2026")
        
        submit_button = st.form_submit_button("✨ Créer l'Événement", type="primary")
        
        if submit_button:
            # Validation
            if not all([title, category, ticker, slug, description, image, icon, resolution_source, series_slug]):
                st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
            else:
                # Préparer les données
                current_time = datetime.now().isoformat() + "Z"
                
                event_data = {
                    "category": category,
                    "closedTime": closed_time.isoformat() + "T00:00:00Z",
                    "commentCount": comment_count,
                    "createdAt": current_time,
                    "creationDate": creation_date.isoformat(),
                    "description": description,
                    "endDate": end_date.isoformat() + "T00:00:00Z",
                    "icon": icon,
                    "image": image,
                    "published_at": current_time,
                    "resolutionSource": resolution_source,
                    "seriesSlug": series_slug,
                    "slug": slug,
                    "startDate": start_date.isoformat() + "T00:00:00Z",
                    "ticker": ticker,
                    "title": title,
                    "updatedAt": current_time,
                    "volume": volume
                }
                
                # Créer l'événement
                result = create_event(event_data)
                
                if result and result.get("success"):
                    st.success(f"✅ Événement créé avec succès! ID: {result.get('data', {}).get('id')}")
                    st.cache_data.clear()
                    time.sleep(2)
                    st.rerun()

# ============================================================================
# PAGE: ASSISTANT IA
# ============================================================================
elif page == "🤖 Assistant IA":
    st.title("🤖 Assistant IA - Interaction en Langage Naturel")
    
    st.markdown("""
    ### 💡 Comment ça marche ?
    1. **Tapez votre requête** en langage naturel
    2. **L'IA analyse** votre intention
    3. **Confirmez l'action** avant exécution
    4. **Résultat** affiché instantanément
    
    **Exemples de requêtes :**
    - *"Montre-moi tous les événements de catégorie Sports"*
    - *"Combien d'événements Crypto avons-nous ?"*
    - *"Trouve les événements avec un volume supérieur à 1 million"*
    - *"Donne-moi les statistiques globales"*
    """)
    
    st.divider()
    
    # Vérifier si la clé API Anthropic est configurée
    if not os.getenv("ANTHROPIC_API_KEY"):
        st.error("""
        ❌ **Clé API Anthropic manquante**
        
        Pour utiliser l'Assistant IA, vous devez configurer votre clé API Anthropic Claude.
        
        **Instructions :**
        1. Créez un compte sur https://console.anthropic.com
        2. Générez une clé API
        3. Ajoutez `ANTHROPIC_API_KEY=votre_clé` dans votre fichier `.env`
        4. Relancez l'application
        """)
    else:
        from ai_assistant import parse_user_intent, execute_intent, generate_natural_response
        
        # Initialiser l'historique de conversation
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        if "pending_intent" not in st.session_state:
            st.session_state.pending_intent = None
        
        # Afficher l'historique
        if st.session_state.chat_history:
            st.subheader("💬 Historique de Conversation")
            for i, msg in enumerate(st.session_state.chat_history):
                if msg["role"] == "user":
                    st.markdown(f"**👤 Vous :** {msg['content']}")
                else:
                    st.markdown(f"**🤖 Assistant :** {msg['content']}")
                st.divider()
        
        # Zone de saisie utilisateur
        user_query = st.text_area(
            "💬 Votre requête :",
            placeholder="Ex: Montre-moi tous les événements Sports avec plus de 100 commentaires",
            height=100,
            key="user_input"
        )
        
        col_btn1, col_btn2 = st.columns([1, 5])
        with col_btn1:
            analyze_btn = st.button("🔍 Analyser", type="primary", use_container_width=True)
        with col_btn2:
            clear_btn = st.button("🗑️ Effacer l'historique", use_container_width=True)
        
        if clear_btn:
            st.session_state.chat_history = []
            st.session_state.pending_intent = None
            st.rerun()
        
        # Analyser la requête
        if analyze_btn and user_query:
            with st.spinner("🤔 Analyse de votre requête..."):
                intent = parse_user_intent(user_query)
                st.session_state.pending_intent = intent
                
                # Ajouter à l'historique
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_query
                })
            
            st.rerun()
        
        # Afficher l'intent pour confirmation
        if st.session_state.pending_intent:
            intent = st.session_state.pending_intent
            
            st.subheader("🎯 Analyse de l'Intention")
            
            # Afficher la confiance
            confidence = intent.get("confidence", 0)
            confidence_color = "green" if confidence > 0.7 else "orange" if confidence > 0.4 else "red"
            st.markdown(f"**Confiance :** :{confidence_color}[{confidence*100:.0f}%]")
            
            # Vérifier si clarification nécessaire
            if intent.get("needs_clarification"):
                st.warning("⚠️ Clarification nécessaire")
                questions = intent.get("clarification_questions", [])
                for q in questions:
                    st.markdown(f"❓ {q}")
                
                if st.button("🔄 Reformuler"):
                    st.session_state.pending_intent = None
                    st.rerun()
            else:
                # Afficher le résumé
                summary = intent.get("summary", {})
                
                col_sum1, col_sum2, col_sum3 = st.columns(3)
                
                with col_sum1:
                    st.info(f"**🎯 QUOI**\n\n{summary.get('what', 'N/A')}")
                
                with col_sum2:
                    st.info(f"**📍 OÙ**\n\n{summary.get('where', 'N/A')}")
                
                with col_sum3:
                    impact = summary.get('impact', 'N/A')
                    impact_emoji = "📖" if "lecture" in impact.lower() else "✏️" if "modification" in impact.lower() or "création" in impact.lower() else "🗑️" if "suppression" in impact.lower() else "📊"
                    st.info(f"**{impact_emoji} IMPACT**\n\n{impact}")
                
                # Afficher les paramètres
                with st.expander("🔧 Paramètres détaillés"):
                    st.json(intent.get("parameters", {}))
                
                st.divider()
                
                # Boutons de confirmation
                col_confirm1, col_confirm2, col_confirm3 = st.columns([2, 2, 3])
                
                with col_confirm1:
                    if st.button("✅ Confirmer et Exécuter", type="primary", use_container_width=True):
                        with st.spinner("⚙️ Exécution en cours..."):
                            result = execute_intent(intent, API_BASE_URL)
                            
                            # Générer réponse naturelle
                            response = generate_natural_response(intent, result)
                            
                            # Ajouter à l'historique
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": response
                            })
                            
                            # Afficher le résultat
                            if result.get("success"):
                                st.success(response)
                                
                                # Afficher les données si pertinent
                                data = result.get("data", {})
                                if isinstance(data, dict):
                                    if "data" in data and isinstance(data["data"], list):
                                        # Liste d'événements
                                        events = data["data"]
                                        if events:
                                            df = pd.DataFrame(events)
                                            display_cols = ["_id", "title", "category", "commentCount", "volume"]
                                            display_cols = [c for c in display_cols if c in df.columns]
                                            st.dataframe(df[display_cols], use_container_width=True)
                                    elif "total_events" in data:
                                        # Statistiques
                                        st.json(data)
                            else:
                                st.error(response)
                            
                            st.session_state.pending_intent = None
                            st.cache_data.clear()
                
                with col_confirm2:
                    if st.button("❌ Annuler", use_container_width=True):
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": "Action annulée par l'utilisateur."
                        })
                        st.session_state.pending_intent = None
                        st.rerun()
                
                with col_confirm3:
                    if st.button("🔄 Modifier la requête", use_container_width=True):
                        st.session_state.pending_intent = None
                        st.rerun()

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 1rem;'>
    <p>📊 Polymarket Dashboard | Powered by FastAPI & Streamlit | 2026</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh
if auto_refresh:
    time.sleep(30)
    st.rerun()
