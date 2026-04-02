import streamlit as st
import pandas as pd
import sqlite3
import bcrypt
import time
import PyPDF2
from database import init_db, login_user, add_user, upgrade_to_premium

# --- INITIALISATION ---
init_db()
st.set_page_config(page_title="LegalOS - Kareem IA", layout="wide")

# --- LOGIQUE INTERNE (Évite les erreurs d'import) ---
def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        return "".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    except: return "Erreur de lecture PDF"

def classifier_procedure(faits):
    if not faits: return "NON DÉFINI", 1
    t = faits.lower()
    if any(w in t for w in ["salaire", "travail", "licenciement", "patron", "prud'hommes"]): 
        return "DROIT DU TRAVAIL", 2
    if any(w in t for w in ["loyer", "bail", "expulsion", "propriétaire", "locataire"]): 
        return "DROIT IMMOBILIER", 3
    return "DROIT CIVIL GÉNÉRAL", 1

def calculer_score(faits, a_des_preuves=False):
    if not faits: return 0
    score = 30
    if len(faits) > 400: score += 20
    if a_des_preuves: score += 40
    return min(score, 98)

# --- DESIGN "LEGALOS GOLD" ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    .main-title { color: #10b981; font-size: 2.5rem; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .kareem-box { 
        background-color: #1e293b; padding: 25px; border-radius: 12px; 
        border-left: 5px solid #10b981; border: 1px solid #334155;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }
    .stMetric { background: #1e293b; padding: 10px; border-radius: 10px; border: 1px solid #334155; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTION DE LA SESSION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- ÉCRAN D'ACCÈS (CONNEXION / INSCRIPTION) ---
if not st.session_state.logged_in:
    st.markdown('<p class="main-title">⚖️ LegalOS Access</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])
    
    with tab1:
        email_login = st.text_input("Email Professionnel", key="login_email")
        pass_login = st.text_input("Mot de passe", type="password", key="login_pass")
        if st.button("Se connecter", key="btn_login"):
            res = login_user(email_login, pass_login)
            if res:
                st.session_state.logged_in = True
                st.session_state.user_name = res[0]
                st.session_state.is_premium = res[2]
                st.rerun()
            else:
                st.error("Identifiants incorrects.")
    
    with tab2:
        st.subheader("Créer un nouveau compte")
        new_name = st.text_input("Nom complet", key="reg_name")
        new_email = st.text_input("Email", key="reg_email")
        new_pass = st.text_input("Mot de passe", type="password", key="reg_pass")
        promo_key = st.text_input("Clé Premium (Optionnel)", key="reg_key")
        
        if st.button("Créer le compte", key="btn_reg"):
            if add_user(new_email, new_pass, new_name):
                if promo_key == "FREEMAN-2026":
                    upgrade_to_premium(new_email)
                st.success("Compte créé avec succès ! Connectez-vous via l'onglet Connexion.")
            else:
                st.error("Erreur : cet email est peut-être déjà utilisé.")
    st.stop()

# --- INTERFACE PRINCIPALE (Dès que connecté) ---

with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user_name}")
    if st.session_state.is_premium:
        st.markdown('<span style="background:#10b981; color:white; padding:4px 10px; border-radius:15px; font-size:12px;">PREMIUM ACCESS</span>', unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📍 MÉTHODE FREEMAN")
    
    steps = [
        "1. Qualification", "2. Objectif", "3. Base Légale", 
        "4. Inventaire", "5. Risques", "6. Amiable", 
        "7. Stratégie", "8. Rédaction", "9. Audience", 
        "10. Jugement", "11. Recours"
    ]
    
    selected_step = st.radio("Navigation du dossier :", steps)
    current_step_num = int(selected_step.split('.')[0])
    
    st.divider()
    if st.button("Se déconnecter"):
        st.session_state.logged_in = False
        st.rerun()

# --- ZONE DE TRAVAIL ---
st.markdown(f'<p style="color:#10b981; font-size:1.8rem; font-weight:bold;">{selected_step}</p>', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    if current_step_num == 1:
        st.subheader("📄 Qualification du Dossier")
        st.write("Décrivez les faits pour que Kareem identifie la procédure.")
        
        file = st.file_uploader("Preuves PDF (Facultatif)", type="pdf")
        faits_text = st.text_area("Récit détaillé des faits :", height=300, placeholder="Ex: Mon employeur refuse de me payer mes heures supplémentaires depuis 3 mois...")
        
        if st.button("🚀 LANCER L'ANALYSE KAREEM"):
            with st.spinner("Analyse Freeman en cours..."):
                final_faits = faits_text
                if file:
                    final_faits += "\n" + extract_text_from_pdf(file)
                
                branch, _ = classifier_procedure(final_faits)
                score = calculer_score(final_faits, a_des_preuves=bool(file))
                
                st.session_state.current_analysis = {
                    "branch": branch,
                    "score": score,
                    "faits": final_faits
                }

    elif current_step_num == 2:
        st.subheader("🎯 Définition de l'Objectif")
        st.info("Cette étape permet de définir ce que vous voulez obtenir (Dommages et intérêts, annulation, etc.)")
        # Logique Étape 2 à venir...

with col_right:
    st.subheader("🤖 Intelligence Kareem")
    if 'current_analysis' in st.session_state:
        ana = st.session_state.current_analysis
        
        c1, c2 = st.columns(2)
        c1.metric("Branche détectée", ana['branch'])
        c2.metric("Chances de succès", f"{ana['score']}%")
        st.progress(ana['score'] / 100)
        
        st.markdown(f"""
        <div class="kareem-box">
            <b>Diagnostic de Qualification :</b><br>
            Le dossier relève du <b>{ana['branch']}</b>.<br><br>
            <i>Analyse stratégique :</i> Vos chances de succès actuelles sont estimées à {ana['score']}%. 
            Pour l'étape suivante (Objectif), Kareem va analyser vos demandes spécifiques.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Veuillez remplir les informations à gauche pour activer l'IA.")
