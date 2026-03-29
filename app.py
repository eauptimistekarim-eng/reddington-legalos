import streamlit as st

# 1. CONFIGURATION (Doit être la toute première commande Streamlit)
st.set_page_config(page_title="LegalOS v1.0", layout="wide", page_icon="⚖️")

# 2. TENTATIVE D'IMPORTATION SÉCURISÉE
try:
    from views.etape_1 import afficher_qualification
except ImportError as e:
    st.error(f"Erreur d'importation : {e}. Vérifiez que le dossier 'views' et le fichier 'etape_1.py' existent.")
    def afficher_qualification(): st.warning("Module de qualification indisponible.")

# 3. DESIGN SYSTÈME (Dark Mode Forcé pour visibilité)
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: white; }
    [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    .step-container {
        background-color: #1e293b;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #334155;
        color: white !important;
    }
    h1, h2, h3, h4, h5, h6, p, span, label { color: white !important; }
    .stTextArea textarea { background-color: #0f172a; color: white !important; border: 1px solid #334155; }
    </style>
    """, unsafe_allow_html=True)

# 4. NAVIGATION SIDEBAR
st.sidebar.title("🧠 LegalOS v1.0")
st.sidebar.markdown("---")

menu_reddington = {
    "1️⃣ Qualification": afficher_qualification,
    "2️⃣ Objectif": lambda: st.info("Étape 2 : Définition de l'objectif stratégique."),
    "3️⃣ Base légale": lambda: st.info("Étape 3 : Recherche des fondements juridiques."),
    "4️⃣ Preuves / Dossier": lambda: st.info("Étape 4 : Inventaire des pièces probantes.")
}

selection = st.sidebar.radio("Protocole Reddington :", list(menu_reddington.keys()))

# 5. ZONE DE TITRE PRINCIPALE
st.title(f"📍 {selection}")

# 6. EXÉCUTION DE L'ÉTAPE
try:
    menu_reddington[selection]()
except Exception as e:
    st.error(f"Erreur d'exécution dans {selection} : {e}")

st.sidebar.markdown("---")
st.sidebar.caption("Moteur Reddington Universel actif")
