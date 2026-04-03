import streamlit as st
import time
from groq import Groq
from database import *

# --- SETUP ---
init_db()
GROQ_KEY = "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"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS - Freeman Method", layout="wide")

# --- UI STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #e2e8f0; }
    .kareem-box { background: #161b22; border-left: 4px solid #10b981; padding: 20px; border-radius: 8px; margin: 10px 0; }
    .stButton>button { width: 100%; border-radius: 5px; background: #10b981; color: white; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- AUTH ---
if not st.session_state.auth:
    st.title("⚖️ LegalOS")
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        e = st.text_input("Email")
        p = st.text_input("Pass", type="password")
        if st.button("Se connecter"):
            res = login_user(e, p)
            if res:
                st.session_state.auth, st.session_state.user_name, st.session_state.user_email = True, res[0], e
                st.rerun()
    with t2:
        n, em, pa = st.text_input("Nom"), st.text_input("Email "), st.text_input("Mdp", type="password")
        if st.button("S'inscrire"):
            if register_user(em, pa, n): st.success("Compte OK")
    st.stop()

# --- NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "cabinet"

if st.session_state.page == "cabinet":
    st.title(f"📂 Cabinet Freeman - {st.session_state.user_name}")
    if st.button("➕ NOUVELLE AFFAIRE"):
        st.session_state.current_dossier = f"Affaire_{int(time.time())}"
        st.session_state.page = "travail"; st.rerun()
    
    for i, d in enumerate(get_user_dossiers(st.session_state.user_email)):
        if st.button(f"📁 {d}", key=f"d_{i}"):
            st.session_state.current_dossier = d
            st.session_state.page = "travail"; st.rerun()
    st.stop()

# --- WORKSPACE ---
with st.sidebar:
    st.header("MÉTHODE FREEMAN")
    if st.button("⬅️ Cabinet"): st.session_state.page = "cabinet"; st.rerun()
    steps = [
        "1. Qualification (Auto)", "2. Objectif (Auto)", "3. Base Légale (Auto)",
        "4. Inventaire & Docs", "5. Analyse des Risques", "6. Procédure Amiable",
        "7. Stratégie (Avocat du Diable)", "8. Rédaction & Modèles", 
        "9. Simulation Audience", "10. Analyse Jugement", "11. Recours"
    ]
    choice = st.radio("Étapes :", steps)
    idx = steps.index(choice) + 1

st.title(f"📌 {choice}")
faits, analyse = get_step_specific_data(st.session_state.user_email, st.session_state.current_dossier, idx)

col1, col2 = st.columns(2)

with col1:
    # Cas spécial : Importation à l'étape 4
    if idx == 4:
        uploaded_file = st.file_uploader("Importer des pièces (PDF, TXT)", type=["pdf", "txt"])
        if uploaded_file: st.info(f"Document {uploaded_file.name} prêt pour analyse.")
    
    input_text = st.text_area("Saisissez vos notes ou éléments bruts :", value=faits, height=400)
    
    if st.button("⚖️ EXÉCUTER PAR KAREEM"):
        full_ctx = get_full_context(st.session_state.user_email, st.session_state.current_dossier)
        
        # LOGIQUE SPECIFIQUE PAR ETAPE
        prompts = {
            1: "Détermine seul la qualification juridique exacte de cette affaire.",
            2: "Détermine les objectifs stratégiques prioritaires pour l'utilisateur.",
            3: "Identifie les textes de loi et la base légale applicable.",
            5: "Identifie tous les risques (financiers, réputation, perte du procès).",
            6: "Rédige une proposition de protocole d'accord amiable.",
            7: "Joue l'AVOCAT DU DIABLE. Anticipe les attaques de l'adversaire et casse nos arguments.",
            8: "Génère un modèle d'acte juridique complet prêt à l'emploi.",
            9: "Simule l'audience. Pose-moi les questions pièges que le juge va poser.",
            10: "Analyse le jugement rendu et explique les points de victoire ou défaite.",
            11: "Propose une solution de recours ou d'appel solide."
        }
        
        mission = prompts.get(idx, "Analyse les données fournies.")
        final_prompt = f"METHODE FREEMAN\nCONTEXTE: {full_ctx}\nMISSION: {mission}\nDONNEES ACTUELLES: {input_text}"
        
        resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": final_prompt}])
        res_text = resp.choices[0].message.content
        save_step_progress(st.session_state.user_email, st.session_state.current_dossier, input_text, res_text, idx)
        st.session_state.last_ia = res_text
        st.rerun()

with col2:
    st.subheader("🤖 Rapport de Kareem")
    ia_val = st.session_state.get('last_ia', analyse)
    if ia_val:
        st.markdown(f'<div class="kareem-box">{ia_val}</div>', unsafe_allow_html=True)
        if idx == 8:
            st.download_button("📥 Télécharger le modèle", ia_val, file_name="acte_juridique.txt")
    else:
        st.info("Kareem attend vos éléments pour agir.")
