# app.py
import streamlit as st

st.set_page_config(page_title="LegalOS - Méthode Freeman", layout="wide", page_icon="⚖️")

# --- CSS PERSONNALISÉ POUR UN DESIGN PREMIUM ---
st.markdown("""
    <style>
    /* Fond principal et police */
    .main { background-color: #0f172a; color: #f8fafc; }
    
    /* Barre latérale */
    section[data-testid="stSidebar"] { background-color: #1e293b !important; border-right: 1px solid #334155; }
    
    /* Titre des étapes */
    .step-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Boutons */
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton>button:hover { background-color: #2563eb; transform: translateY(-1px); }
    
    /* Zones de texte */
    .stTextArea textarea { background-color: #1e293b; color: white; border: 1px solid #334155; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if "etape_actuelle" not in st.session_state:
    st.session_state.etape_actuelle = 1

# --- SIDEBAR FIXE ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3437/3437295.png", width=80) # Icône balance
    st.title("Kareem AI")
    st.markdown("*LegalOS Edition*")
    st.divider()
    
    progression = st.session_state.etape_actuelle / 11
    st.progress(progression)
    st.write(f"📈 **Progression : {int(progression*100)}%**")
    st.caption(f"Étape {st.session_state.etape_actuelle} sur 11")
    
    st.divider()
    if st.session_state.get("branche_active"):
        st.success(f"📍 {st.session_state.branche_active}")
    
    if st.button("🔄 Nouvelle Analyse"):
        st.session_state.clear()
        st.rerun()

# --- DISPATCHER DE CONTENU ---
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
    st.error(f"⚠️ Erreur d'affichage : {e}")
