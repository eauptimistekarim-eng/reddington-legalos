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

# --- FONCTIONS UTILES ---
def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        return "".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    except: return "Erreur de lecture PDF"

def classifier_procedure(faits):
    if not faits: return "NON DÉFINI", 1
    t = faits.lower()
    if any(w in t for w in ["salaire", "travail", "licenciement", "patron", "prud'hommes"]): return "DROIT DU TRAVAIL", 2
    if any(w in t for w in ["loyer", "bail", "expulsion", "propriétaire", "locataire"]): return "DROIT IMMOBILIER", 3
    return "DROIT CIVIL GÉNÉRAL", 1

def calculer_score(faits, a_des_preuves=False):
    if not faits: return 0
    score = 30
    if len(faits) > 400: score += 20
    if a_des_preuves: score += 40
    return min(score, 98)

# --- DESIGN ---
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

# --- AUTHENTIFICATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<p class="main-title">⚖️ LegalOS Access</p>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        e = st.text_input("Email", key="l_e")
        p = st.text_input("Mot de passe", type="password", key="l_p")
        if st.button("Se connecter"):
            res = login_user(e, p)
            if res:
                st.session_state.logged_in, st.session_state.user_name, st.session_state.is_premium = True, res[0], res[2]
                st.rerun()
            else: st.error("Identifiants invalides")
    with t2:
        # Code inscription simplifié ici
        st.info("Utilisez vos identifiants existants.")
    st.stop()

# --- NAVIGATION SIDEBAR ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user_name}")
    st.divider()
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", "5. Risques", "6. Amiable", "7. Stratégie", "8. Rédaction", "9. Audience", "10. Jugement", "11. Recours"]
    selected_step = st.radio("MÉTHODE FREEMAN", steps)
    idx = int(selected_step.split('.')[0])
    if st.button("Se déconnecter"):
        st.session_state.logged_in = False
        st.rerun()

# --- CONTENU PRINCIPAL ---
st.markdown(f'<p style="color:#10b981; font-size:1.8rem; font-weight:bold;">{selected_step}</p>', unsafe_allow_html=True)
col_l, col_r = st.columns([1, 1], gap="large")

with col_l:
    if idx == 1:
        st.subheader("📄 Qualification des Faits")
        st.radio("État du dossier :", ["Nouveau dossier", "Dossier en cours", "À finaliser", "Terminé"], horizontal=True)
        f = st.file_uploader("Preuves PDF", type="pdf")
        txt = st.text_area("Récit des faits :", height=250)
        if st.button("🚀 LANCER L'ANALYSE"):
            b, _ = classifier_procedure(txt)
            s = calculer_score(txt, bool(f))
            st.session_state.ana = {"branch": b, "score": s}
            
    elif idx == 2:
        st.subheader("🎯 Définition de l'Objectif")
        branch = st.session_state.get('ana', {}).get('branch', 'DROIT CIVIL')
        objs = {
            "DROIT DU TRAVAIL": ["Contester un licenciement", "Rappel de salaires", "Harcèlement"],
            "DROIT IMMOBILIER": ["Récupérer caution", "Expulsion", "Travaux non faits"]
        }.get(branch, ["Dommages et intérêts", "Exécution de contrat"])
        choix = st.selectbox("L'IA propose ces objectifs :", objs)
        st.text_area("Détails supplémentaires :")
        if st.button("Valider l'objectif"): st.success("Objectif enregistré.")

    elif idx == 3:
        st.subheader("⚖️ Base Légale & Jurisprudence")
        st.write("Génération des articles de loi basés sur les étapes 1 et 2...")
        if st.button("Générer les textes"):
            st.info("Article L1232-1 du Code du travail identifié.")

    elif idx == 4:
        st.subheader("🔐 Inventaire (Le Coffre-fort)")
        st.file_uploader("Uploadez toutes vos pièces justificatives", accept_multiple_files=True)
        if st.button("Extraire les infos"): st.success("Analyse des documents terminée.")

    # ... Logique pour étapes 5 à 11 à compléter selon le même modèle ...

with col_r:
    st.subheader("🤖 Intelligence Kareem")
    if 'ana' in st.session_state:
        st.metric("Branche", st.session_state.ana['branch'])
        st.metric("Succès estimé", f"{st.session_state.ana['score']}%")
        st.markdown(f'<div class="kareem-box"><b>Conseil Freeman :</b> Passez à l\'étape {idx+1} pour renforcer le dossier.</div>', unsafe_allow_html=True)
    else:
        st.info("En attente de l'analyse étape 1...")
