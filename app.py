# app.py
import streamlit as st
from database import init_db, add_user, login_user, charger_dossier, sauvegarder_dossier

# 1. CONFIG
st.set_page_config(page_title="LegalOS | Méthode Freeman", layout="wide", page_icon="⚖️")
init_db()

# 2. CSS MIDNIGHT FIXÉ (Supprime le carré gris inutile)
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #e2e8f0; }
    
    /* Cacher le header Streamlit par défaut */
    header {visibility: hidden;}
    
    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #020617 !important; border-right: 1px solid #1e293b; }
    
    /* Conteneur principal sans marges fantômes */
    .content-card {
        background: #1e293b; 
        padding: 2rem; 
        border-radius: 15px; 
        border: 1px solid #334155;
        margin-top: 0px;
    }

    .step-banner { 
        background: #1e293b; 
        padding: 1.5rem; 
        border-radius: 15px; 
        border-left: 6px solid #3b82f6; 
        margin-bottom: 1rem; 
    }
    
    .stButton>button { 
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); 
        color: white; border: none; border-radius: 10px; font-weight: 600; 
    }
    </style>
""", unsafe_allow_html=True)

# 3. AUTHENTIFICATION
if "user_auth" not in st.session_state:
    st.session_state.user_auth = False

if not st.session_state.user_auth:
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        st.markdown('<div style="background:#1e293b; padding:3rem; border-radius:20px; border:1px solid #334155; margin-top:20%;">', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center; color:white;'>⚖️ LegalOS</h1>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Connexion", "Inscription"])
        with t1:
            e = st.text_input("Email", key="l_email")
            p = st.text_input("Mot de passe", type="password", key="l_pwd")
            if st.button("Accéder", use_container_width=True):
                user = login_user(e, p)
                if user:
                    st.session_state.user_auth, st.session_state.user_email = True, e
                    st.session_state.user_name, st.session_state.user_role = user[0], user[1]
                    d = charger_dossier(e)
                    st.session_state.etape_actuelle = d[0] if d else 1
                    st.rerun()
        with t2:
            n = st.text_input("Nom")
            em = st.text_input("Email")
            pw = st.text_input("Pass", type="password")
            if st.button("Créer", use_container_width=True):
                if add_user(em, pw, n): st.success("OK")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 4. SIDEBAR
with st.sidebar:
    st.markdown(f"<div style='text-align:center; padding:1rem; background:#0f172a; border-radius:15px; border:1px solid #334155;'><div style='font-size:1.5rem;'>👤</div><div style='color:white; font-weight:bold;'>{st.session_state.user_name}</div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    etapes = ["1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", "9. Audience", "10. Jugement", "11. Exécution"]
    for i, nom in enumerate(etapes, 1):
        if st.button(f"{'🎯' if i == st.session_state.etape_actuelle else '  '} {nom}", key=f"nav_{i}", use_container_width=True):
            st.session_state.etape_actuelle = i
            st.rerun()
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.user_auth = False
        st.rerun()

# 5. CONTENU (Sans le carré gris)
_, col_main, _ = st.columns([1, 8, 1])
with col_main:
    st.markdown(f"<div class='step-banner'><h2 style='color:white; margin:0;'>Étape {st.session_state.etape_actuelle} : {etapes[st.session_state.etape_actuelle-1]}</h2></div>", unsafe_allow_html=True)
    
    # Début de la carte de contenu
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
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
        else: st.info("Module en cours...")
    except Exception as e: st.error(f"Erreur : {e}")
    st.markdown('</div>', unsafe_allow_html=True) # Fin de la carte

# 6. NAVIGATION BAS DE PAGE
st.markdown("<br>", unsafe_allow_html=True)
b1, _, b3 = st.columns([2, 6, 2])
with b1:
    if st.session_state.etape_actuelle > 1:
        if st.button("⬅️ PRÉCÉDENT", use_container_width=True):
            st.session_state.etape_actuelle -= 1
            st.rerun()
with b3:
    if st.session_state.etape_actuelle < 11:
        if st.button("SUIVANT ➡️", use_container_width=True):
            sauvegarder_dossier(st.session_state.user_email, st.session_state.etape_actuelle + 1, st.session_state.get('faits_bruts', ''), st.session_state.get('branche_active', ''))
            st.session_state.etape_actuelle += 1
            st.rerun()
