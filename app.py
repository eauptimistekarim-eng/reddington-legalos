# app.py
import streamlit as st

# Importation de tes 11 étapes (Assure-toi que les fichiers existent dans views/)
from views.etape_1 import afficher_qualification # Supposant que l'étape 1 est là
from views.etape_2 import afficher_objectif
from views.etape_3 import afficher_base_legale
from views.etape_4 import afficher_administration_preuve
from views.etape_5 import afficher_avocat_diable
from views.etape_6 import afficher_decision_action
from views.etape_7 import afficher_relance_amiable
from views.etape_8 import afficher_mise_en_demeure
from views.etape_9 import afficher_saisie_tribunal
from views.etape_10 import afficher_preparation_audience
from views.etape_11 import afficher_rapport_final

# Configuration du Design
st.set_page_config(page_title="LegalOS - Méthode Freeman", layout="wide", page_icon="⚖️")

# --- CSS POUR FIXER L'INTERFACE ---
st.markdown("""
    <style>
    .step-header { background-color: #1e3a8a; color: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; font-size: 1.5rem; font-weight: bold; }
    .stButton>button { border-radius: 5px; height: 3em; transition: 0.3s; }
    .stButton>button:hover { background-color: #3b82f6; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DE LA SESSION ---
if "etape_actuelle" not in st.session_state:
    st.session_state.etape_actuelle = 1

# --- BARRE LATÉRALE (NAVIGATION & PROGRESSION) ---
with st.sidebar:
    st.title("⚖️ Kareem (LegalOS)")
    st.subheader("Méthode Freeman")
    
    progression = st.session_state.etape_actuelle / 11
    st.progress(progression)
    st.write(f"📊 Étape {st.session_state.etape_actuelle} / 11")
    
    st.divider()
    if st.button("🔄 Réinitialiser l'audit"):
        st.session_state.clear()
        st.rerun()

# --- DISPATCHER DE CONTENU (L'AIGUILLAGE) ---
# Ici, on affiche l'étape correspondante à l'état de la session
if st.session_state.etape_actuelle == 1:
    # Si tu n'as pas encore le fichier etape_1, on met un placeholder
    try: afficher_qualification()
    except: st.write("Étape 1 : Qualification du litige (Récit)")

elif st.session_state.etape_actuelle == 2:
    afficher_objectif()

elif st.session_state.etape_actuelle == 3:
    afficher_base_legale()

elif st.session_state.etape_actuelle == 4:
    afficher_administration_preuve()

elif st.session_state.etape_actuelle == 5:
    afficher_avocat_diable()

elif st.session_state.etape_actuelle == 6:
    afficher_decision_action()

elif st.session_state.etape_actuelle == 7:
    afficher_relance_amiable()

elif st.session_state.etape_actuelle == 8:
    afficher_mise_en_demeure()

elif st.session_state.etape_actuelle == 9:
    afficher_saisie_tribunal()

elif st.session_state.etape_actuelle == 10:
    afficher_preparation_audience()

elif st.session_state.etape_actuelle == 11:
    afficher_rapport_final()
