import streamlit as st
import pandas as pd
import time
import PyPDF2
from database import init_db, login_user, add_user, upgrade_to_premium

# --- INITIALISATION ---
init_db()
st.set_page_config(page_title="LegalOS - Kareem IA", layout="wide")

# --- EFFET MACHINE À ÉCRIRE ---
def typewriter(text, speed=0.02):
    container = st.empty()
    displayed_text = ""
    for char in text:
        displayed_text += char
        container.markdown(f'<div class="kareem-box">{displayed_text}▌</div>', unsafe_allow_html=True)
        time.sleep(speed)
    container.markdown(f'<div class="kareem-box">{displayed_text}</div>', unsafe_allow_html=True)

# --- LOGIQUE MÉTIER ---
def classifier_procedure(faits):
    if not faits: return "NON DÉFINI"
    t = faits.lower()
    if any(w in t for w in ["salaire", "travail", "licenciement", "patron"]): return "DROIT DU TRAVAIL"
    if any(w in t for w in ["loyer", "bail", "expulsion"]): return "DROIT IMMOBILIER"
    return "DROIT CIVIL GÉNÉRAL"

# --- DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    .kareem-box { 
        background-color: #161e2e; padding: 20px; border-radius: 10px; 
        border-left: 4px solid #10b981; font-family: 'Courier New', Courier, monospace;
        color: #10b981; line-height: 1.5; font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- AUTHENTIFICATION (SIMPLIFIÉE POUR LE TEST) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    # (Garder ton code de connexion habituel ici)
    if st.button("Simuler Connexion (Test)"): 
        st.session_state.logged_in = True
        st.session_state.user_name = "Karim"
        st.rerun()
    st.stop()

# --- MÉMOIRE DES ÉTAPES (Lien entre elles) ---
if 'dossier' not in st.session_state:
    st.session_state.dossier = {
        "faits": "", "branche": "Non définie", "objectif": "", "loi": ""
    }

# --- NAVIGATION ---
with st.sidebar:
    st.title("⚖️ LegalOS")
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire"]
    choice = st.radio("MÉTHODE FREEMAN", steps)
    idx = int(choice.split('.')[0])

# --- INTERFACE PRINCIPALE ---
col_l, col_r = st.columns([1, 1], gap="large")

with col_l:
    st.subheader(f"📍 {choice}")
    
    if idx == 1:
        txt = st.text_area("Racontez les faits du dossier :", height=200)
        if st.button("Analyser la Qualification"):
            st.session_state.dossier["faits"] = txt
            st.session_state.dossier["branche"] = classifier_procedure(txt)
            st.session_state.trigger_kareem = True

    elif idx == 2:
        if not st.session_state.dossier["faits"]:
            st.warning("⚠️ Retournez à l'étape 1 pour qualifier les faits.")
        else:
            st.write(f"Branche : **{st.session_state.dossier['branche']}**")
            obj = st.selectbox("Choisissez l'objectif :", ["Dommages et Intérêts", "Annulation de contrat"])
            if st.button("Fixer l'objectif"):
                st.session_state.dossier["objectif"] = obj
                st.session_state.trigger_kareem = True

with col_r:
    st.subheader("🤖 Kareem IA")
    if st.session_state.get('trigger_kareem'):
        if idx == 1:
            msg = f"Analyse en cours... \n\nJ'ai identifié que ce dossier relève du {st.session_state.dossier['branch']}. \n\nC'est un bon début. Passons à l'étape 2 pour définir ce que nous allons exiger."
        elif idx == 2:
            msg = f"Très bien. Pour un dossier de {st.session_state.dossier['branch']}, viser l'objectif '{st.session_state.dossier['objectif']}' est stratégique. \n\nPréparons maintenant la base légale à l'étape 3."
        
        typewriter(msg)
        st.session_state.trigger_kareem = False
    else:
        st.info("Kareem attend vos instructions...")
