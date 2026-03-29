import streamlit as st

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="LegalOS | Méthode Freeman", layout="wide", page_icon="⚖️")

# --- 2. SYSTÈME DE SESSION POUR LE COMPTE ---
if "user_auth" not in st.session_state:
    st.session_state.user_auth = False
    st.session_state.user_name = "Utilisateur"
    st.session_state.user_role = "Visiteur"

# --- 3. DESIGN SYSTÈME (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    
    /* Profil Utilisateur dans la Sidebar */
    .user-profile {
        padding: 1.5rem;
        background: #1e293b;
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid #334155;
        text-align: center;
    }
    .user-avatar {
        width: 60px;
        height: 60px;
        background: #3b82f6;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 10px auto;
        font-size: 24px;
        font-weight: bold;
        color: white;
    }
    .user-info h4 { color: white !important; margin: 0; font-size: 1rem; }
    .user-info p { color: #94a3b8; font-size: 0.8rem; margin: 0; }

    /* Bandeau d'étape */
    .step-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white; padding: 2.5rem; border-radius: 15px; margin-bottom: 2rem;
    }
    
    /* Carte de contenu */
    .content-card {
        background: white; padding: 2.5rem; border-radius: 12px; 
        border: 1px solid #e2e8f0; margin-bottom: 5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR AVEC PROFIL ET NAVIGATION ---
with st.sidebar:
    # BLOC PROFIL UTILISATEUR
    st.markdown(f"""
        <div class="user-profile">
            <div class="user-avatar">{st.session_state.user_name[0].upper()}</div>
            <div class="user-info">
                <h4>{st.session_state.user_name}</h4>
                <p>{st.session_state.user_role}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # CONNEXION / DÉCONNEXION SIMULÉE
    if not st.session_state.user_auth:
        if st.button("🔑 Se connecter / S'inscrire", use_container_width=True):
            # Ici on pourrait ouvrir un formulaire, on simule pour le design
            st.session_state.user_auth = True
            st.session_state.user_name = "Kévin Freeman"
            st.session_state.user_role = "Membre Premium"
            st.rerun()
    else:
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.user_auth = False
            st.session_state.user_name = "Utilisateur"
            st.session_state.user_role = "Visiteur"
            st.rerun()

    st.divider()
    
    # NAVIGATION (LES 11 ÉTAPES)
    INFOS_ETAPES = {
        1: "Qualification", 2: "Objectif", 3: "Base légale", 4: "Preuves", 
        5: "Stratégie", 6: "Amiable", 7: "Procédure", 8: "Rédaction", 
        9: "Audience", 10: "Jugement", 11: "Exécution"
    }

    for i in range(1, 12):
        style = "✅" if i < st.session_state.get('etape_actuelle', 1) else "🎯" if i == st.session_state.get('etape_actuelle', 1) else "⚪"
        if st.button(f"{style} {i}. {INFOS_ETAPES[i]}", key=f"nav_{i}", use_container_width=True):
            st.session_state.etape_actuelle = i
            st.rerun()

# --- 5. LOGIQUE D'ACCÈS (VÉRIFICATION DE CONNEXION) ---
col1, col_content, col3 = st.columns([1, 8, 1])

with col_content:
    if not st.session_state.user_auth:
        # ÉCRAN DE BIENVENUE SI NON CONNECTÉ
        st.markdown("""
            <div style="text-align: center; padding: 5rem;">
                <h1>Bienvenue sur LegalOS ⚖️</h1>
                <p style="font-size: 1.2rem; color: #64748b;">Veuillez vous connecter pour accéder à la Méthode Freeman et commencer votre analyse juridique.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # AFFICHAGE DE L'ÉTAPE SI CONNECTÉ
        etape = st.session_state.get('etape_actuelle', 1)
        st.markdown(f"""
            <div class="step-banner">
                <h1>{etape}. {INFOS_ETAPES[etape]}</h1>
                <p>Analyse et gestion de votre dossier en temps réel.</p>
            </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            # Appel des fichiers views ici
            st.write(f"Contenu de l'étape {etape}...")
            st.markdown('</div>', unsafe_allow_html=True)

# --- 6. NAVIGATION BAS DE PAGE ---
if st.session_state.user_auth:
    st.divider()
    cb1, cb2, cb3 = st.columns([2, 6, 2])
    with cb1:
        if st.session_state.get('etape_actuelle', 1) > 1:
            if st.button("⬅️ PRÉCÉDENT", use_container_width=True):
                st.session_state.etape_actuelle -= 1
                st.rerun()
    with cb3:
        if st.session_state.get('etape_actuelle', 1) < 11:
            if st.button("SUIVANT ➡️", use_container_width=True):
                st.session_state.etape_actuelle += 1
                st.rerun()
