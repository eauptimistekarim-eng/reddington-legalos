import streamlit as st
import pandas as pd
from database import init_db, login_user, add_user, upgrade_to_premium
from processor import extract_text_from_pdf, classifier_procedure_universelle, calculer_score_victoire, get_freeman_prompt
import time

# --- INITIALISATION ---
init_db()
st.set_page_config(page_title="LegalOS - Kareem IA", layout="wide", initial_sidebar_state="expanded")

# --- DESIGN FIXE "LEGALOS GOLD" ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    .main-title { color: #10b981; font-size: 2.5rem; font-weight: bold; margin-bottom: 20px; text-align: center; }
    .kareem-box { 
        background-color: #1e293b; padding: 20px; border-radius: 12px; 
        border-left: 5px solid #10b981; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        margin-top: 15px; line-height: 1.6;
    }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .status-badge { padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTION DE SESSION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_data' not in st.session_state: st.session_state.user_data = None
if 'current_step' not in st.session_state: st.session_state.current_step = 1

# --- ÉCRAN DE CONNEXION ---
if not st.session_state.logged_in:
    st.markdown('<p class="main-title">⚖️ LegalOS Access</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Connexion", "Inscription / Clé Premium"])
    
    with tab1:
        email = st.text_input("Email Professionnel")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Accéder au Cabinet"):
            result = login_user(email, password)
            if result:
                st.session_state.logged_in = True
                st.session_state.user_data = {"name": result[0], "role": result[1], "premium": result[2], "email": email}
                st.success(f"Bienvenue, Maître {result[0]}")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Identifiants incorrects.")

    with tab2:
        new_name = st.text_input("Nom Complet")
        new_email = st.text_input("Email")
        new_pw = st.text_input("Créer un mot de passe", type="password")
        access_key = st.text_input("Clé d'activation unique (Premium)")
        
        if st.button("Créer mon compte"):
            if add_user(new_email, new_pw, new_name):
                if access_key == "FREEMAN-2026": # Ta clé à usage unique
                    upgrade_to_premium(new_email)
                st.success("Compte créé ! Connectez-vous.")
            else:
                st.error("Cet email est déjà utilisé.")
    st.stop()

# --- INTERFACE PRINCIPALE (Post-Connexion) ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user_data['name']}")
    if st.session_state.user_data['premium']:
        st.markdown('<span style="background:#10b981; color:white; padding:2px 8px; border-radius:10px;">PREMIUM</span>', unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📁 Gestion du Dossier")
    # Menu basé sur tes notes : Nouveau, En cours, Finalisé, Terminé
    status = st.selectbox("Statut du dossier", ["NOUVEAU DOSSIER", "DOSSIER EN COURS", "À FINALISER", "TERMINÉ"])
    
    st.divider()
    st.subheader("📍 Étapes Freeman")
    step_options = {
        1: "1. Qualification", 2: "2. Objectif", 3: "3. Base Légale",
        4: "4. Inventaire", 5: "5. Risques", 6: "6. Amiable",
        7: "7. Stratégie", 8: "8. Rédaction", 9: "9. Audience",
        10: "10. Jugement", 11: "11. Recours"
    }
    selected_step = st.radio("Navigation", list(step_options.values()), index=st.session_state.current_step-1)
    st.session_state.current_step = int(selected_step.split('.')[0])

# --- CONTENU DES ÉTAPES ---
st.markdown(f'# {selected_step}')

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📥 Saisie des éléments")
    
    if st.session_state.current_step == 1:
        uploaded_file = st.file_uploader("Glisser un PDF (Contrat, Courrier...)", type="pdf")
        user_text = st.text_area("Faits et éléments du dossier :", height=300, placeholder="Décrivez les faits ici...")
        
        if uploaded_file:
            pdf_text = extract_text_from_pdf(uploaded_file)
            user_text += f"\n\n--- CONTENU DU PDF ---\n{pdf_text}"
            
        if st.button("🚀 LANCER L'ANALYSE KAREEM"):
            with st.spinner("Kareem analyse le dossier..."):
                # Simulation de l'appel IA (à lier à ta fonction processor)
                branche, _ = classifier_procedure_universelle(user_text)
                score = calculer_score_victoire(user_text, branche, a_des_preuves=bool(uploaded_file))
                
                st.session_state['last_analysis'] = {
                    "branche": branche,
                    "score": score,
                    "text": f"Analyse Freeman terminée pour l'étape {selected_step}."
                }

    elif st.session_state.current_step == 2:
        st.info("🎯 L'IA va maintenant déterminer l'objectif selon la qualification de l'étape 1.")
        # Ici on ajoutera la logique pour proposer des objectifs à choisir (ton schéma étape 2)

with col_right:
    st.subheader("🤖 Analyse de Kareem")
    if 'last_analysis' in st.session_state:
        ana = st.session_state['last_analysis']
        
        # Dashboard de l'IA
        c1, c2 = st.columns(2)
        c1.metric("Branche", ana['branche'])
        c2.metric("Succès estimé", f"{ana['score']}%")
        st.progress(ana['score']/100)
        
        st.markdown(f'<div class="kareem-box">{ana["text"]}</div>', unsafe_allow_html=True)
    else:
        st.info("En attente de données pour lancer Kareem...")
