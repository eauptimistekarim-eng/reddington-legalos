# app.py
import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="LegalOS - Méthode Freeman",
    layout="wide",
    page_icon="⚖️"
)

# --- DESIGN CSS FIXE (STYLE WINDOWS) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .step-header { 
        background-color: #1e3a8a; 
        color: white; 
        padding: 1.5rem; 
        border-radius: 10px; 
        margin-bottom: 2rem; 
        font-size: 1.4rem;
        font-weight: bold;
        border-left: 8px solid #3b82f6;
    }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DE LA SESSION ---
if "etape_actuelle" not in st.session_state:
    st.session_state.etape_actuelle = 1
if "branche_active" not in st.session_state:
    st.session_state.branche_active = "Non définie"

# --- BARRE LATÉRALE (FIXE) ---
with st.sidebar:
    st.title("⚖️ Kareem (LegalOS)")
    st.subheader("Méthode Freeman")
    
    # Barre de progression
    progression = st.session_state.etape_actuelle / 11
    st.progress(progression)
    st.write(f"📊 Progression : {int(progression*100)}% (Étape {st.session_state.etape_actuelle}/11)")
    
    st.divider()
    st.info(f"📍 Branche détectée : \n**{st.session_state.branche_active}**")
    
    st.divider()
    if st.button("🔄 Réinitialiser l'Audit"):
        st.session_state.clear()
        st.rerun()

# --- AIGUILLAGE DYNAMIQUE (LE CŒUR DE L'APP) ---
# On importe et affiche l'étape correspondante
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

except ImportError as e:
    st.error(f"Erreur : Impossible de charger l'étape {st.session_state.etape_actuelle}.")
    st.info(f"Détail technique : {e}")
    st.warning("Vérifiez que vos fichiers sont bien nommés et placés dans le dossier 'views'.")
