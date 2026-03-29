# app.py
import streamlit as st

st.set_page_config(page_title="LegalOS - Méthode Freeman", layout="wide", page_icon="⚖️")

# --- CSS POUR LE DESIGN ET LE FOOTER FIXE ---
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    section[data-testid="stSidebar"] { background-color: #1e293b !important; }
    .step-header { background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; color: white; }
    
    /* Style pour la barre de navigation en bas */
    .nav-container {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #1e293b;
        padding: 10px 50px;
        border-top: 1px solid #334155;
        display: flex;
        justify-content: space-between;
        z-index: 1000;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if "etape_actuelle" not in st.session_state:
    st.session_state.etape_actuelle = 1

# --- SIDEBAR ---
with st.sidebar:
    st.title("Kareem AI")
    progression = st.session_state.etape_actuelle / 11
    st.progress(progression)
    st.write(f"Étape {st.session_state.etape_actuelle} / 11")
    st.divider()
    if st.button("🔄 Nouvelle Analyse"):
        st.session_state.clear()
        st.rerun()

# --- DISPATCHER DE CONTENU ---
# (Tes imports d'étapes ici...)
try:
    if st.session_state.etape_actuelle == 1:
        from views.etape_1 import afficher_qualification
        afficher_qualification()
    elif st.session_state.etape_actuelle == 2:
        from views.etape_2 import afficher_objectif
        afficher_objectif()
    # ... (les autres elif de 3 à 11)
except Exception as e:
    st.error(f"Erreur : {e}")

# --- BARRE DE NAVIGATION (BOUTONS PRÉCÉDENT / SUIVANT) ---
st.markdown("<br><br><br>", unsafe_allow_html=True) # Espace pour ne pas cacher le contenu
st.divider()
col_prev, col_spacer, col_next = st.columns([1, 3, 1])

with col_prev:
    if st.session_state.etape_actuelle > 1:
        if st.button("⬅️ PRÉCÉDENT"):
            st.session_state.etape_actuelle -= 1
            st.rerun()

with col_next:
    if st.session_state.etape_actuelle < 11:
        # On ne permet d'avancer que si certaines données sont présentes (optionnel)
        if st.button("SUIVANT ➡️"):
            st.session_state.etape_actuelle += 1
            st.rerun()
