# app.py
import streamlit as st
from views.etape_2 import afficher_objectif
from views.etape_3 import afficher_base_legale

st.set_page_config(page_title="LegalOS - Méthode Freeman", layout="wide")

# --- INITIALISATION DE LA MÉMOIRE (SESSION STATE) ---
if "etape_actuelle" not in st.session_state:
    st.session_state.etape_actuelle = 2 # On commence ici pour ton test
if "branche_active" not in st.session_state:
    st.session_state.branche_active = "💼 DROIT DES AFFAIRES" # Test par défaut
if "montant_estime" not in st.session_state:
    st.session_state.montant_estime = 1000

# --- BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.title("⚖️ LegalOS")
    st.subheader("Méthode Freeman")
    progression = (st.session_state.etape_actuelle / 11)
    st.progress(progression)
    st.write(f"Progression : {int(progression*100)}%")
    
    st.divider()
    st.write(f"📍 Branche : **{st.session_state.branche_active}**")

# --- AFFICHAGE DYNAMIQUE DES ÉTAPES ---
if st.session_state.etape_actuelle == 2:
    afficher_objectif()
elif st.session_state.etape_actuelle == 3:
    afficher_base_legale()
elif st.session_state.etape_actuelle == 4:
    st.success("🎉 Vous êtes à l'étape 4 : Administration de la preuve.")
    if st.button("Retour à l'étape 3"):
        st.session_state.etape_actuelle = 3
        st.rerun()
