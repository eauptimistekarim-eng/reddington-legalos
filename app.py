import streamlit as st
from database import init_db, add_user, login_user

# 1. CONFIGURATION & THÈME
st.set_page_config(page_title="LegalOS | Méthode Freeman", layout="wide", page_icon="⚖️")
init_db()

# 2. DESIGN "MIDNIGHT" (CSS)
st.markdown("""
    <style>
    /* Fond global sombre et doux */
    .stApp {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    
    /* Login Container */
    .login-container {
        max-width: 450px;
        margin: 5% auto;
        padding: 3rem;
        background: #1e293b;
        border-radius: 20px;
        border: 1px solid #334155;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }

    /* Style des inputs pour le mode sombre */
    input {
        background-color: #0f172a !important;
        color: white !important;
        border: 1px solid #334155 !important;
    }

    /* Bouton Primaire */
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        font-weight: 600;
    }

    /* Sidebar stylisée */
    section[data-testid="stSidebar"] {
        background-color: #020617 !important;
        border-right: 1px solid #1e293b;
    }

    /* Banner d'étape */
    .step-banner {
        background: #1e293b;
        padding: 2rem;
        border-radius: 15px;
        border-left: 6px solid #3b82f6;
        margin-bottom: 2rem;
    }
    
    /* Carte de contenu */
    .content-card {
        background: #1e293b;
        padding: 2.5rem;
        border-radius: 15px;
        border: 1px solid #334155;
        min-height: 400px;
    }

    /* Tabs (Connexion/Inscription) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #3b82f6;
    }
    </style>
""", unsafe_allow_html=True)

# 3. LOGIQUE D'AUTHENTIFICATION
if "user_auth" not in st.session_state:
    st.session_state.user_auth = False

if not st.session_state.user_auth:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:white;'>⚖️ LegalOS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8;'>Connectez-vous à votre espace juridique</p>", unsafe_allow_html=True)
    
    tab_log, tab_reg = st.tabs(["Connexion", "Créer un compte"])
    
    with tab_log:
        e = st.text_input("Email", key="l_email")
        p = st.text_input("Mot de passe", type="password", key="l_pwd")
        if st.button("Accéder au système", use_container_width=True):
            user = login_user(e, p)
            if user:
                st.session_state.user_auth = True
                st.session_state.user_name = user[0]
                st.session_state.user_role = user[1]
                st.session_state.etape_actuelle = 1
                st.rerun()
            else:
                st.error("Email ou mot de passe incorrect.")
                
    with tab_reg:
        n = st.text_input("Nom complet")
        em = st.text_input("Email (identifiant)", key="r_email")
        pw = st.text_input("Mot de passe", type="password", key="r_pwd")
        if st.button("Finaliser l'inscription", use_container_width=True):
            if add_user(em, pw, n):
                st.success("Compte créé ! Connectez-vous.")
            else:
                st.error("Erreur : cet email existe déjà.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 4. SIDEBAR (Navigation & Profil)
with st.sidebar:
    st.markdown(f"""
        <div style='text-align:center; padding: 1rem; background:#0f172a; border-radius:15px; border:1px solid #334155;'>
            <div style='font-size: 2rem;'>👤</div>
            <div style='color:white; font-weight:bold; font-size:1.1rem;'>{st.session_state.user_name}</div>
            <div style='color:#3b82f6; font-size:0.8rem;'>{st.session_state.user_role}</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    etapes = [
        "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", 
        "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", 
        "9. Audience", "10. Jugement", "11. Exécution"
    ]
    
    for i, nom in enumerate(etapes, 1):
        # Indicateur visuel
        if st.button(f"{'🎯' if i == st.session_state.etape_actuelle else '  '} {nom}", key=f"nav_{i}", use_container_width=True):
            st.session_state.etape_actuelle = i
            st.rerun()

    st.divider()
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.user_auth = False
        st.rerun()

# 5. ZONE DE TRAVAIL CENTRALE
col_l, col_c, col_r = st.columns([1, 8, 1])

with col_c:
    # Bannière d'étape
    st.markdown(f"""
        <div class="step-banner">
            <h2 style='color:white; margin:0;'>Étape {st.session_state.etape_actuelle} : {etapes[st.session_state.etape_actuelle-1]}</h2>
            <p style='color:#94a3b8; margin:5px 0 0 0;'>Méthode Freeman appliquée</p>
        </div>
    """, unsafe_allow_html=True)

    # Carte de contenu logicielle
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    # CHARGEMENT DES MODULES (Correction des imports ici)
    try:
        if st.session_state.etape_actuelle == 1:
            from views.etape_1 import afficher_qualification
            afficher_qualification()
        elif st.session_state.etape_actuelle == 2:
            from views.etape_2 import afficher_objectif
            afficher_objectif()
        else:
            st.info(f"Le module {st.session_state.etape_actuelle} est prêt pour l'intégration.")
    except Exception as e:
        st.error(f"Erreur d'exécution : {e}")

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
            st.session_state.etape_actuelle += 1
            st.rerun()
