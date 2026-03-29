import streamlit as st
from views.etape_2 import afficher_objectif
from views.etape_3 import afficher_base_legale
from views.etape_4 import afficher_administration_preuve

st.set_page_config(page_title="LegalOS - Méthode Freeman", layout="wide")

# --- STYLE CSS POUR FIXER LE DESIGN ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold; }
    .step-header { background-color: #1e3a8a; color: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if "etape_actuelle" not in st.session_state:
    st.session_state.etape_actuelle = 2
if "branche_active" not in st.session_state:
    st.session_state.branche_active = "💼 DROIT DES AFFAIRES"

# --- SIDEBAR FIXE ---
with st.sidebar:
    st.title("⚖️ LegalOS")
    st.subheader("Méthode Freeman")
    progression = st.session_state.etape_actuelle / 11
    st.progress(progression)
    st.write(f"📊 Étape {st.session_state.etape_actuelle} sur 11")
    st.divider()
    st.info(f"📍 Dossier : {st.session_state.get('branche_active', 'En cours...')}")

# --- ZONE DE CONTENU DYNAMIQUE ---
# Seule cette partie change quand on clique sur "Suivant"
if st.session_state.etape_actuelle == 2:
    afficher_objectif()
elif st.session_state.etape_actuelle == 3:
    afficher_base_legale()
elif st.session_state.etape_actuelle == 4:
    afficher_administration_preuve()
