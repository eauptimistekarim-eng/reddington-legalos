import streamlit as st
from database import init_db, add_user, login_user # Import de ton fichier database.py

# 1. INITIALISATION
st.set_page_config(page_title="LegalOS | Méthode Freeman", layout="wide", page_icon="⚖️")
init_db()

# 2. DESIGN CSS (L'identité visuelle de ton logiciel)
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    
    /* Login Box */
    .login-container {
        max-width: 450px; margin: auto; padding: 2rem;
        background: white; border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;
        margin-top: 10%;
    }

    /* Profil Utilisateur Sidebar */
    .user-card {
        padding: 1rem; background: #1e293b; border-radius: 12px;
        border: 1px solid #334155; text-align: center; margin-bottom: 1.5rem;
    }
    .avatar {
        width: 50px; height: 50px; background: #3b82f6;
        border-radius: 50%; display: flex; align-items: center;
        justify-content: center; margin: 0 auto 10px; color: white; font-weight: bold;
    }

    /* Bandeau d'étape */
    .step-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# 3. GESTION DE L'AUTHENTIFICATION
if "user_auth" not in st.session_state:
    st.session_state.user_auth = False

if not st.session_state.user_auth:
    # --- ÉCRAN DE CONNEXION ---
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.title("⚖️ Accès LegalOS")
    tab_log, tab_reg = st.tabs(["Connexion", "Créer un compte"])
    
    with tab_log:
        e = st.text_input("Email", key="l_email")
        p = st.text_input("Mot de passe", type="password", key="l_pwd")
        if st.button("Se connecter", use_container_width=True):
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
        em = st.text_input("Email", key="r_email")
        pw = st.text_input("Mot de passe", type="password", key="r_pwd")
        if st.button("S'inscrire", use_container_width=True):
            if add_user(em, pw, n):
                st.success("Compte créé ! Connectez-vous.")
            else:
                st.error("Erreur : cet email existe déjà.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 4. SIDEBAR (Navigation & Profil)
with st.sidebar:
    # Affichage du profil
    st.markdown(f"""
        <div class="user-card">
            <div class="avatar">{st.session_state.user_name[0].upper()}</div>
            <div style="color:white; font-weight:bold;">{st.session_state.user_name}</div>
            <div style="color:#94a3b8; font-size:0.8rem;">{st.session_state.user_role}</div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.user_auth = False
        st.rerun()
    
    st.divider()
    
    # Menu des 11 étapes
    etapes = [
        "1. Qualification", "2. Objectif", "3. Base légale", "4. Preuves", 
        "5. Stratégie", "6. Amiable", "7. Procédure", "8. Rédaction", 
        "9. Audience", "10. Jugement", "11. Exécution"
    ]
    
    for i, nom in enumerate(etapes, 1):
        # Indicateur visuel
        label = f"{'🎯' if i == st.session_state.etape_actuelle else '⚪'} {nom}"
        if st.button(label, key=f"nav_{i}", use_container_width=True):
            st.session_state.etape_actuelle = i
            st.rerun()

# 5. CONTENU CENTRAL
col1, col_center, col3 = st.columns([1, 8, 1])

with col_center:
    # Titre dynamique vulgarisé
    titres_vulgarises = {
        1: "Comprendre votre situation", 2: "Définir ce que vous voulez", 
        3: "Trouver vos droits", 4: "Rassembler vos preuves" # etc...
    }
    
    st.markdown(f"""
        <div class="step-banner">
            <h1 style='color:white;'>Étape {st.session_state.etape_actuelle} : {etapes[st.session_state.etape_actuelle-1]}</h1>
            <p>{titres_vulgarises.get(st.session_state.etape_actuelle, "Analyse en cours...")}</p>
        </div>
    """, unsafe_allow_html=True)

    # Zone d'affichage des fichiers views/
    try:
        if st.session_state.etape_actuelle == 1:
            from views.etape_1 import afficher_qualification
            afficher_qualification()
        elif st.session_state.etape_actuelle == 2:
            from views.etape_2 import afficher_objectif
            afficher_objectif()
        # On ajoutera les autres ici...
    except Exception as e:
        st.info(f"Le module {st.session_state.etape_actuelle} est prêt pour l'intégration des fonctions.")

# 6. NAVIGATION BAS DE PAGE
st.divider()
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
