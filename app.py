import streamlit as st
from views.etape_1 import afficher_etape_1

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="Fortas OS",
    layout="wide",
    page_icon="⚖️"
)

# 2. DESIGN GLOBAL (Forçage des couleurs pour lisibilité maximale)
st.markdown("""
    <style>
    /* Fond de l'application */
    .main { background-color: #f4f7f9; }
    
    /* Cartes blanches avec texte noir forcé */
    .css-card {
        background-color: white !important;
        border-radius: 12px;
        padding: 25px;
        border: 1px solid #e0e6ed;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        color: #1a1a1a !important;
    }
    
    /* Zones de texte avec scroll interne */
    .scroll-box {
        height: 500px;
        overflow-y: auto;
        padding: 15px;
        background-color: #ffffff !important;
        border: 1px solid #f0f2f6;
        line-height: 1.6;
        font-size: 1rem;
        color: #1a1a1a !important;
        white-space: pre-wrap;
    }
    
    /* Titres de sections Bleus */
    .section-title {
        color: #1E3A8A !important;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 15px;
        text-transform: uppercase;
        border-bottom: 2px solid #3B82F6;
        padding-bottom: 5px;
        display: inline-block;
    }
    
    /* Boutons Fortas avec dégradé */
    .stButton>button {
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        color: white !important;
        border: none;
        font-weight: 600;
        border-radius: 8px;
        height: 3.5em;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(30,58,138,0.3);
    }
    
    /* Forcer le noir sur tous les textes Markdown dans les colonnes */
    div[data-testid="stMarkdownContainer"] p {
        color: #1a1a1a !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. NAVIGATION LATÉRALE (Dictionnaire des étapes)
st.sidebar.title("⚖️ Fortas OS")

# On définit ici les fonctions à appeler pour chaque menu
etapes = {
    "1. Qualification": afficher_etape_1,
    "2. Chronologie": lambda: st.info("Module Chronologie (Étape 2) : En attente d'intégration."),
    "3. Validité": lambda: st.info("Module Validité (Étape 3) : En attente d'intégration."),
    "4. Inventaire": lambda: st.info("Module Inventaire (Étape 4) : Prêt pour le développement."),
    "5. Calculs": lambda: st.info("Module Calculs (Étape 5) : En attente.")
}

choix = st.sidebar.radio("Navigation du Protocole :", list(etapes.keys()))

# 4. AFFICHAGE DYNAMIQUE
# On affiche le titre de l'étape sélectionnée
st.markdown(f"## 📍 {choix}")

# On exécute la fonction associée au choix
etapes[choix]()
