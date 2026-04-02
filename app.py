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

# --- LOGIQUE INTERNE ---
def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        return "".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    except: return "Erreur de lecture PDF"

def classifier_procedure(faits):
    if not faits: return "NON DÉFINI", 1
    t = faits.lower()
    if any(w in t for w in ["salaire", "travail", "licenciement", "patron"]): return "DROIT DU TRAVAIL", 2
    if any(w in t for w in ["loyer", "bail", "expulsion"]): return "DROIT IMMOBILIER", 3
    return "DROIT CIVIL GÉNÉRAL", 1

def calculer_score(faits, a_des_preuves=False):
    if not faits: return 0
    score = 30
    if len(faits) > 400: score += 20
    if a_des_preuves: score += 40
    return min(score, 98)

# --- DESIGN FIXE ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    .main-title { color: #10b981; font-size: 2.5rem; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .kareem-box { 
        background-color: #1e293b; padding: 25px; border-radius: 12px; 
        border-left: 5px solid #10b981; border: 1px solid #334155;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTION DE LA CONNEXION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<p class="main-title">⚖️ LegalOS Access</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])
    
    with tab1:
        email_input = st.text_input("Email Professionnel")
        pass_input = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            res = login_user(email_input, pass_input)
            if res:
                st.session_state.logged_in = True
                st.session_state.user_name = res[0]
                st.session_state.is_premium = res[2]
                st.rerun()
            else:
                st.error("Identifiants incorrects.")
    
    with tab2:
        st.info("Utilisez l'onglet Inscription pour créer un compte si ce n'est pas déjà fait.")
    st.stop()

# --- SI CONNECTÉ : AFFICHAGE DE LA PAGE D'ACCUEIL ---

# 1. Barre latérale (Sidebar) avec les 11 étapes
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user_name}")
    if st.session_state.is_premium:
        st.markdown('<span style="color:#10b981;">● Mode Premium Activé</span>', unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📍 MÉTHODE FREEMAN")
    
    steps = [
        "1. Qualification", "2. Objectif", "3. Base Légale", 
        "4. Inventaire", "5. Risques", "6. Amiable", 
        "7. Stratégie", "8. Rédaction", "9. Audience", 
        "10. Jugement", "11. Recours"
    ]
    
    selected_step = st.radio("Navigation du dossier :", steps)
    
    st.divider()
    if st.button("Déconnexion"):
        st.session_state.logged_in = False
        st.rerun()

# 2. Zone de travail (Main Page)
current_step_num = int(selected_step.split('.')[0])

st.markdown(f'<p style="color:#10b981; font-size:1.8rem; font-weight:bold;">{selected_step}</p>', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    if current_step_num == 1:
        st.subheader("📄 Qualification du Dossier")
        st.write("Commencez par importer vos preuves ou décrire les faits.")
        
        file = st.file_uploader("Preuves PDF (Facultatif)", type="pdf")
        faits_text = st.text_area("Récit détaillé des faits :", height=300, placeholder="Ex: Mon employeur ne m'a pas versé mon salaire de mars...")
        
        if st.button("🚀 LANCER L'ANALYSE KAREEM"):
            with st.spinner("Kareem analyse la situation..."):
                final_faits = faits_text
                if file:
                    final_faits += "\n" + extract_text_from_pdf(file)
                
                # Calculs
                branch, _ = classifier_procedure(final_faits)
                score = calculer_score(final_faits, a_des_preuves=bool(file))
                
                # Sauvegarde en mémoire pour l'affichage
                st.session_state.current_analysis = {
                    "branch": branch,
                    "score": score,
                    "faits": final_faits
                }

with col_right:
    st.subheader("🤖 Analyse de Kareem")
    if 'current_analysis' in st.session_state:
        ana = st.session_state.current_analysis
        
        st.metric("Branche détectée", ana['branch'])
        st.metric("Score de réussite", f"{ana['score']}%")
        st.progress(ana['score'] / 100)
        
        st.markdown(f"""
        <div class="kareem-box">
            <b>Rapport de Maître Kareem :</b><br><br>
            Le dossier est qualifié en <b>{ana['branch']}</b>.<br><br>
            Sur la base de vos éléments, j'estime vos chances de succès à {ana['score']}%.
            <br><br>
            <i>Conseil :</i> Pour augmenter ce score, assurez-vous d'avoir des preuves écrites tangibles à l'étape 4.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Veuillez remplir les faits à gauche pour activer l'IA.")
