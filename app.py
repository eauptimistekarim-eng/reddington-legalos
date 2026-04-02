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
    if any(w in t for w in ["salaire", "travail", "licenciement", "patron"]): return "DROIT DU TRAVAIL", 2
    if any(w in t for w in ["loyer", "bail", "expulsion"]): return "DROIT IMMOBILIER", 3
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
        border-left: 5px solid #10b981; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }
    .stMetric { background: #1e293b; padding: 10px; border-radius: 10px; border: 1px solid #334155; }
    </style>
    """, unsafe_allow_html=True)

# --- AUTHENTIFICATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<p class="main-title">⚖️ LegalOS Access</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])
    with tab1:
        e = st.text_input("Email")
        p = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            res = login_user(e, p)
            if res:
                st.session_state.logged_in = True
                st.session_state.user = {"name": res[0], "premium": res[2]}
                st.rerun()
            else: st.error("Identifiants invalides")
    with tab2:
        n = st.text_input("Nom")
        em = st.text_input("Email ")
        pw = st.text_input("Mot de passe ", type="password")
        key = st.text_input("Clé Premium (Optionnel)")
        if st.button("Créer le compte"):
            if add_user(em, pw, n):
                if key == "FREEMAN-2026": upgrade_to_premium(em)
                st.success("Compte créé !")
    st.stop()

# --- INTERFACE PRINCIPALE ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user['name']}")
    if st.session_state.user['premium']:
        st.markdown('<span style="background:#10b981; color:white; padding:4px 10px; border-radius:15px; font-size:12px;">PREMIUM ACCESS</span>', unsafe_allow_html=True)
    st.divider()
    
    # Navigation des 11 étapes selon tes notes
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", 
             "5. Risques", "6. Amiable", "7. Stratégie", "8. Rédaction", 
             "9. Audience", "10. Jugement", "11. Recours"]
    choice = st.sidebar.radio("PLAN DE PROCÉDURE", steps)
    current_idx = int(choice.split('.')[0])

# --- CONTENU DYNAMIQUE ---
st.markdown(f'<p style="color:#10b981; font-size:1.5rem; font-weight:bold;">📍 {choice}</p>', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("📝 Éléments du Dossier")
    if current_idx == 1:
        up = st.file_uploader("Preuves PDF", type="pdf")
        txt = st.text_area("Récit des faits", height=300, placeholder="Expliquez la situation ici...")
        
        if st.button("🚀 LANCER L'ANALYSE KAREEM"):
            with st.spinner("Analyse Freeman en cours..."):
                final_text = txt
                if up: final_text += "\n" + extract_text_from_pdf(up)
                
                branch, _ = classifier_procedure(final_text)
                score = calculer_score(final_text, a_des_preuves=bool(up))
                
                st.session_state.analysis = {"branch": branch, "score": score, "step": choice}

with col_right:
    st.subheader("🤖 Intelligence Kareem")
    if 'analysis' in st.session_state:
        ana = st.session_state.analysis
        c1, c2 = st.columns(2)
        c1.metric("Branche", ana['branch'])
        c2.metric("Réussite", f"{ana['score']}%")
        st.progress(ana['score']/100)
        
        st.markdown(f"""
        <div class="kareem-box">
            <b>Rapport de Qualification :</b><br>
            Le dossier est identifié comme relevant du <b>{ana['branch']}</b>.<br><br>
            <i>Conseil Stratégique :</i> Sur la base des faits fournis, votre score de victoire est de {ana['score']}%. 
            Passez à l'étape 2 pour définir l'objectif juridique précis.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Saisissez les données à gauche pour activer l'IA.")
