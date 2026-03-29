import streamlit as st
from views.etape_1 import afficher_qualification
# Nous importerons les autres étapes (2 à 11) ici au fur et à mesure

# 1. CONFIGURATION DE L'OS
st.set_page_config(page_title="LegalOS - Reddington Protocol", layout="wide", page_icon="⚖️")

# 2. DESIGN SYSTÈME (Compatible Light/Dark Mode & Anti-Bug Visuel)
st.markdown("""
    <style>
    /* Global Background */
    .main { background-color: #f8fafc; }
    
    /* Conteneur d'étape (Card) */
    .step-container {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 2rem;
        color: #1e293b; /* Bleu nuit très foncé pour lecture parfaite */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Titre d'étape */
    .step-title {
        color: #1e3a8a;
        font-size: 1.5rem;
        font-weight: 800;
        text-transform: uppercase;
        border-bottom: 3px solid #3b82f6;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }

    /* Bouton d'Action Primaire */
    .stButton>button {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white !important;
        border-radius: 8px;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 700;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. NAVIGATION LATÉRALE (Les 11 Étapes Reddington)
st.sidebar.title("🧠 LegalOS v1.0")
st.sidebar.markdown("---")

menu_reddington = {
    "1️⃣ Qualification": afficher_qualification,
    "2️⃣ Objectif": lambda: st.info("Définition de l'objectif..."),
    "3️⃣ Base légale": lambda: st.info("Recherche de la base légale..."),
    "4️⃣ Preuves / Dossier": lambda: st.info("Inventaire des pièces..."),
    "5️⃣ Analyse stratégique": lambda: st.info("Calcul des risques..."),
    "6️⃣ Phase amiable": lambda: st.info("Mise en demeure & Négociation..."),
    "7️⃣ Choix de procédure": lambda: st.info("Sélection de la voie judiciaire..."),
    "8️⃣ Rédaction juridique": lambda: st.info("Génération d'actes..."),
    "9️⃣ Audience": lambda: st.info("Préparation de la plaidoirie..."),
    "🔟 Jugement": lambda: st.info("Analyse de la décision..."),
    "1️⃣1️⃣ Exécution / Recours": lambda: st.info("Voies d'exécution & Appel...")
}

selection = st.sidebar.radio("Protocole Reddington :", list(menu_reddington.keys()))

# 4. ZONE D'AFFICHAGE DYNAMIQUE
with st.container():
    # On force l'encapsulation dans notre style CSS
    st.markdown(f'<div class="step-title">{selection}</div>', unsafe_allow_html=True)
    
    # On appelle la fonction correspondant à l'étape
    menu_reddington[selection]()

st.sidebar.markdown("---")
st.sidebar.caption("Propulsé par le moteur de règles universel LegalOS")
