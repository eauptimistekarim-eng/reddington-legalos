# app.py
import streamlit as st
from database import init_db, add_user, login_user, charger_dossier, sauvegarder_dossier

# 1. INITIALISATION
st.set_page_config(page_title="LegalOS | Méthode Freeman", layout="wide", page_icon="⚖️")
init_db()

# 2. DESIGN MIDNIGHT PRO
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #e2e8f0; }
    section[data-testid="stSidebar"] { background-color: #020617 !important; border-right: 1px solid #1e293b; }
    .login-container { max-width: 450px; margin: 5% auto; padding: 3rem; background: #1e293b; border-radius: 20px; border: 1px solid #334155; }
    .step-banner { background: #1e293b; padding: 2rem; border-radius: 15px; border-left: 6px solid #3b82f6; margin-bottom: 2rem; }
    .content-card { background: #1e293b; padding: 2.5rem; border-radius: 15px; border: 1px solid #334155; min-height: 400px; }
    .stButton>button { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; border: none; border-radius: 10px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# 3. AUTHENTIFICATION
if "user_auth" not in st.session_state:
    st.session_state.user_auth = False

if not st.session_state.user_auth:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:white;'>⚖️ LegalOS</h1>", unsafe_allow_html=True)
    tab_log, tab_reg = st.tabs(["Connexion", "Créer un compte"])
    with tab_log:
        e = st.text_input("Email", key="l_email")
        p = st.text_input("Mot de passe", type="password", key="l_pwd")
        if st.button("Accéder au système", use_container_width=True):
            user = login_user(e, p)
            if user:
                st.session_state.user_auth = True
                st.session_state.user_email = e
                st.session_state.user_name = user[0]
                st.session_state.user_role = user[1]
                data = charger_dossier(e)
                if data:
                    st.session_state.etape_actuelle = data[0]
                    st.session_state.faits_bruts = data[1]
                    st.session_state.branche_active = data[2]
                else: st.session_state.etape_actuelle = 1
                st.rerun()
            else: st.error("Identifiants incorrects.")
    with tab_reg:
        n = st.text_input("Nom complet")
        em = st.text_input("Email")
        pw = st.text_input("Mot de passe", type="password")
        if st.button("S'inscrire", use_container_width=True):
            if add_user(em, pw, n): st.success("Compte créé !")
            else: st.error("Email déjà utilisé.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 4. SIDEBAR & NAVIGATION
with st.sidebar:
    st.markdown(f"<div style='text-align:center; padding: 1rem; background:#0f172a; border-radius:15px; border:1px solid #334155;'><div style='font-size: 1.5rem;'>👤</div><div style='color:white; font-weight:bold;'>{st.session_state.user_name}</div><div style='color:#3b82f6; font-size:0.8rem;'>{st.session_state.user_role}</div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    etapes = ["1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", "9. Audience", "10. Jugement", "11. Exécution"]
    for i, nom in enumerate(etapes, 1):
        if st.button(f"{'🎯' if i == st.session_state.etape_actuelle else '  '} {nom}", key=f"nav_{i}", use_container_width=True):
            st.session_state.etape_actuelle = i
            st.rerun()
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.user_auth = False
        st.rerun()

# 5. CONTENU
col_l, col_c, col_r = st.columns([1, 8, 1])
with col_c:
    st.markdown(f"<div class='step-banner'><h2 style='color:white; margin:0;'>Étape {st.session_state.etape_actuelle} : {etapes[st.session_state.etape_actuelle-1]}</h2></div>", unsafe_allow_html=True)
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
        else: st.info("Module en développement...")
    except Exception as e: st.error(f"Erreur : {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# 6. NAVIGATION BAS DE PAGE
st.markdown("<br>", unsafe_allow_html=True)
b1, b2, b3 = st.columns([2, 6, 2])
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
