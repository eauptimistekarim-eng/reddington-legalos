# app.py
import streamlit as st

# Configuration de la page
st.set_page_config(page_title="LegalOS - Méthode Freeman", layout="wide", page_icon="⚖️")

# --- DESIGN CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    /* Fond et texte */
    .main { background-color: #0f172a; color: #f8fafc; }
    
    /* Header des étapes */
    .step-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 30px;
        border-left: 8px solid #60a5fa;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #1e293b !important; border-right: 1px solid #334155; }
    
    /* Boutons de navigation */
    .nav-button {
        display: flex;
        justify-content: space-between;
        margin-top: 50px;
        padding: 20px;
        background-color: #1e293b;
        border-top: 1px solid #334155;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTION DE LA SESSION ---
if "etape_actuelle" not in st.session_state:
    st.session_state.etape_actuelle = 1

# --- SIDEBAR (NAVIGATION FIXE) ---
with st.sidebar:
    st.title("⚖️ Kareem AI")
    st.subheader("Méthode Freeman")
    st.divider()
    
    # Indicateur de progression
    prog = st.session_state.etape_actuelle / 11
    st.progress(prog)
    st.write(f"📊 Étape **{st.session_state.etape_actuelle}** / 11")
    
    if st.session_state.get("branche_active"):
        st.info(f"Dossier : **{st.session_state.branche_active}**")
    
    st.divider()
    if st.button("🔄 Nouvelle Analyse"):
        st.session_state.clear()
        st.rerun()

# --- AFFICHAGE DYNAMIQUE DES ÉTAPES ---
# Note : Chaque fonction afficher_X doit exister dans tes fichiers views/
try:
    if st.session_state.etape_actuelle == 1:
        from views.etape_1 import afficher_qualification
        afficher_qualification()
    elif st.session_state.etape_actuelle == 2:
        from views.etape_2 import afficher_objectif
        afficher_objectif()
    elif st.session_state.etape_actuelle == 3:
        from views.etape_3 import afficher_base_legale
        afficher_base_legale()
    elif st.session_state.etape_actuelle == 4:
        from views.etape_4 import afficher_administration_preuve
        afficher_administration_preuve()
    elif st.session_state.etape_actuelle == 5:
        from views.etape_5 import afficher_avocat_diable
        afficher_avocat_diable()
    elif st.session_state.etape_actuelle == 6:
        from views.etape_6 import afficher_decision_action
        afficher_decision_action()
    elif st.session_state.etape_actuelle == 7:
        from views.etape_7 import afficher_relance_amiable
        afficher_relance_amiable()
    elif st.session_state.etape_actuelle == 8:
        from views.etape_8 import afficher_mise_en_demeure
        afficher_mise_en_demeure()
    elif st.session_state.etape_actuelle == 9:
        from views.etape_9 import afficher_saisie_tribunal
        afficher_saisie_tribunal()
    elif st.session_state.etape_actuelle == 10:
        from views.etape_10 import afficher_preparation_audience
        afficher_preparation_audience()
    elif st.session_state.etape_actuelle == 11:
        from views.etape_11 import afficher_rapport_final
        afficher_rapport_final()
except Exception as e:
    st.error(f"Erreur de chargement : {e}")

# --- BOUTONS DE NAVIGATION BAS DE PAGE ---
st.divider()
col_prev, col_next = st.columns([1, 1])
with col_prev:
    if st.session_state.etape_actuelle > 1:
        if st.button("⬅️ Étape Précédente"):
            st.session_state.etape_actuelle -= 1
            st.rerun()
with col_next:
    if st.session_state.etape_actuelle < 11:
        if st.button("Étape Suivante ➡️"):
            st.session_state.etape_actuelle += 1
            st.rerun()
