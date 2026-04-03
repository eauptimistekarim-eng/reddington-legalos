import streamlit as st
import time
from groq import Groq
from database import *
from pypdf import PdfReader # Pour l'analyse de documents

# --- CONFIG ---
init_db()
GROQ_KEY = "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"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS - Méthode Freeman", layout="wide")

# --- UI ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #e2e8f0; }
    .kareem-box { background: #161b22; border-left: 5px solid #10b981; padding: 25px; border-radius: 10px; margin-bottom: 20px; }
    .slogan { text-align: center; color: #94a3b8; font-style: italic; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# Persistence Session
if 'auth' not in st.session_state: st.session_state.auth = False

def extract_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# --- LOGIN (LE BLOCAGE S'ARRÊTE ICI) ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>⚖️ LegalOS</h1>", unsafe_allow_html=True)
    st.markdown("<p class='slogan'>Système Expert de la Méthode Freeman</p>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])
    with tab1:
        with st.form("login_f"):
            email = st.text_input("Email")
            pw = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Entrer dans le Cabinet"):
                user_info = login_user(email, pw)
                if user_info:
                    st.session_state.auth = True
                    st.session_state.user_name = user_info[0]
                    st.session_state.user_email = email
                    st.rerun()
                else: st.error("Échec de connexion. Vérifiez vos accès.")
    with tab2:
        with st.form("reg_f"):
            nom = st.text_input("Nom")
            em = st.text_input("Email")
            pwp = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Créer le compte"):
                if register_user(em, pwp, nom): st.success("Compte créé ! Connectez-vous.")
    st.stop()

# --- NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "cabinet"

if st.session_state.page == "cabinet":
    st.title(f"📂 Cabinet Freeman | {st.session_state.user_name}")
    if st.button("➕ NOUVEAU DOSSIER"):
        st.session_state.current_dossier = f"Affaire_{int(time.time())}"
        st.session_state.page = "travail"; st.rerun()
    
    st.divider()
    for i, d in enumerate(get_user_dossiers(st.session_state.user_email)):
        if st.button(f"📁 {d}", key=f"btn_{i}"):
            st.session_state.current_dossier = d
            st.session_state.page = "travail"; st.rerun()
    
    if st.sidebar.button("🚪 Déconnexion"):
        st.session_state.auth = False; st.rerun()
    st.stop()

# --- WORKSPACE FREEMAN ---
with st.sidebar:
    st.title("MÉTHODE FREEMAN")
    if st.button("⬅️ Menu Principal"): st.session_state.page = "cabinet"; st.rerun()
    steps = [
        "1. Qualification (IA Solo)", "2. Objectif (IA Solo)", "3. Base Légale (IA Solo)",
        "4. Inventaire & Analyse Docs", "5. Analyse des Risques", "6. Solution Amiable",
        "7. Stratégie (Avocat du Diable)", "8. Rédaction & Modèles", 
        "9. Simulation d'Audience", "10. Analyse Jugement", "11. Recours"
    ]
    choice = st.radio("Séquence :", steps)
    idx = steps.index(choice) + 1

st.header(f"💼 Dossier : {st.session_state.current_dossier}")
faits_load, analyse_load = get_step_specific_data(st.session_state.user_email, st.session_state.current_dossier, idx)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader(f"📝 Saisie : {choice}")
    
    # Gestion spécifique Etape 4 (Documents)
    doc_text = ""
    if idx == 4:
        up = st.file_uploader("Importer une preuve (PDF)", type="pdf")
        if up: doc_text = "\n[CONTENU DU DOCUMENT IMPORTE]: " + extract_pdf(up)
    
    input_txt = st.text_area("Notes ou éléments bruts :", value=faits_load, height=350)
    
    if st.button("⚡ ACTION KAREEM"):
        full_ctx = get_full_context(st.session_state.user_email, st.session_state.current_dossier)
        
        # Logique de mission par étape
        missions = {
            1: "Détermine seul la qualification juridique précise de l'affaire.",
            2: "Définis seul les objectifs stratégiques prioritaires.",
            3: "Détermine seul la base légale (articles, codes) applicable.",
            4: "Analyse les éléments saisis et les documents fournis pour l'inventaire.",
            5: "Évalue les risques financiers et judiciaires de l'affaire.",
            6: "Rédige une proposition de protocole d'accord amiable ferme.",
            7: "Joue l'AVOCAT DU DIABLE : Détruis les arguments de l'utilisateur pour le tester.",
            8: "Génère un modèle juridique (Assignation, Conclusions) prêt à copier.",
            9: "Simule le Juge : Pose les 3 questions les plus dures à l'utilisateur.",
            10: "Analyse le jugement rendu que l'utilisateur vient de te décrire.",
            11: "Propose une stratégie de recours ou d'appel immédiate."
        }
        
        prompt = f"""Tu es Kareem, Directeur Juridique Expert. Méthode Freeman.
        CONTEXTE HISTORIQUE : {full_ctx}
        MISSION ÉTAPE {idx} : {missions.get(idx)}
        NOTES ACTUELLES : {input_txt} {doc_text}
        CONSIGNE : Sois direct, prends le lead, ne demande pas d'avis, ordonne la marche à suivre."""
        
        resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        res_text = resp.choices[0].message.content
        save_step_progress(st.session_state.user_email, st.session_state.current_dossier, input_txt, res_text, idx)
        st.session_state.last_ia = res_text
        st.rerun()

with col2:
    st.subheader("🤖 Rapport Kareem")
    txt_ia = st.session_state.get('last_ia', analyse_load)
    if txt_ia:
        st.markdown(f'<div class="kareem-box">{txt_ia}</div>', unsafe_allow_html=True)
        if idx == 8: # Exportable en étape 8
            st.download_button("📥 Télécharger le modèle", txt_ia, file_name="Modele_Freeman.txt")
    else:
        st.info("Kareem attend vos éléments.")
