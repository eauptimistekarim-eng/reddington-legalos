import streamlit as st
from views.etape_1 import afficher_qualification

# CONFIGURATION
st.set_page_config(page_title="LegalOS v1.0", layout="wide", page_icon="⚖️")

# DESIGN SYSTÈME
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: white; }
    [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    .step-container { background-color: #1e293b; padding: 25px; border-radius: 12px; border: 1px solid #334155; }
    h1, h2, h3, p, span, label { color: white !important; }
    .stTextArea textarea { background-color: #0f172a; color: white !important; border: 1px solid #334155; }
    .stButton>button { background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); color: white !important; border: none; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# SIDEBAR : LES 11 ÉTAPES REDDINGTON
st.sidebar.title("🧠 LegalOS v1.0")
st.sidebar.markdown("---")

# On prépare les fonctions pour chaque étape (on les créera au fur et à mesure)
menu_reddington = {
    "1️⃣ Qualification": afficher_qualification,
    "2️⃣ Objectif": lambda: st.info("🎯 Étape 2 : Définition de l'objectif stratégique (en développement)."),
    "3️⃣ Base légale": lambda: st.info("📚 Étape 3 : Fondements juridiques et visas (en développement)."),
    "4️⃣ Preuves / Dossier": lambda: st.info("📁 Étape 4 : Inventaire des pièces (en développement)."),
    "5️⃣ Analyse stratégique": lambda: st.info("📈 Étape 5 : Chances de succès et risques (en développement)."),
    "6️⃣ Phase amiable": lambda: st.info("🤝 Étape 6 : Protocoles de négociation (en développement)."),
    "7️⃣ Choix de procédure": lambda: st.info("⚖️ Étape 7 : Sélection de la juridiction (en développement)."),
    "8️⃣ Rédaction juridique": lambda: st.info("✍️ Étape 8 : Génération d'actes (en développement)."),
    "9️⃣ Audience": lambda: st.info("🗣️ Étape 9 : Préparation de la plaidoirie (en développement)."),
    "🔟 Jugement": lambda: st.info("🏛️ Étape 10 : Analyse du dispositif (en développement)."),
    "1️⃣1️⃣ Exécution / Recours": lambda: st.info("🔄 Étape 11 : Voies d'exécution (en développement).")
}

selection = st.sidebar.radio("Protocole Reddington :", list(menu_reddington.keys()))

st.title(f"📍 {selection}")

# EXECUTION
try:
    menu_reddington[selection]()
except Exception as e:
    st.error(f"Erreur : {e}")

st.sidebar.markdown("---")
st.sidebar.caption("Moteur Reddington Universel actif")
