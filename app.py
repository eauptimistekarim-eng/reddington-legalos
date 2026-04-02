import streamlit as st
import time
import re
from database import init_db, login_user, add_user, send_welcome_email

init_db()
st.set_page_config(page_title="LegalOS - Kareem IA", layout="wide")

# --- DESIGN & CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .kareem-box { 
        background-color: #161e2e; padding: 20px; border-radius: 12px; 
        border-left: 4px solid #10b981; font-family: 'Courier New', monospace;
        color: #10b981; border: 1px solid #1e293b; box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .folder-btn { margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTEUR JURIDIQUE MULTI-CODES ---
def analyse_universelle_kareem(faits):
    f = faits.lower()
    # Droit Pénal
    if any(w in f for w in ["vol", "agression", "plainte", "police", "crime", "escroquerie"]):
        return "DROIT PÉNAL", "Code Pénal", "Article 121-1", "Chaque infraction nécessite un élément matériel et un élément moral. Nous devons vérifier la qualification pénale des faits."
    # Droit de la Consommation
    elif any(w in f for w in ["achat", "remboursement", "garantie", "site marchand", "rétractation"]):
        return "DROIT DE LA CONSOMMATION", "Code de la Consommation", "Article L221-18", "Le consommateur dispose d'un droit de rétractation de 14 jours. J'analyse si le délai est respecté."
    # Droit du Travail
    elif any(w in f for w in ["salaire", "licenciement", "patron", "cdi", "cdd"]):
        return "DROIT DU TRAVAIL", "Code du Travail", "Article L1232-1", "Tout licenciement doit être fondé sur une cause réelle et sérieuse. Vérifions la procédure."
    # Droit Commercial
    elif any(w in f for w in ["facture", "fournisseur", "société", "concurrence"]):
        return "DROIT COMMERCIAL", "Code de Commerce", "Article L441-10", "Les pénalités de retard sont exigibles sans qu'un rappel soit nécessaire."
    # Par défaut : Droit Civil
    else:
        return "DROIT CIVIL", "Code Civil", "Article 1240", "Tout fait quelconque de l'homme qui cause à autrui un dommage oblige celui par la faute duquel il est arrivé à le réparer."

# --- TYPEWRITER EFFECT ---
def typewriter(text):
    container = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        container.markdown(f'<div class="kareem-box">🤖 <b>Kareem :</b><br>{displayed}▌</div>', unsafe_allow_html=True)
        time.sleep(0.01)
    container.markdown(f'<div class="kareem-box">🤖 <b>Kareem :</b><br>{displayed}</div>', unsafe_allow_html=True)

# --- LOGIQUE DE NAVIGATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = "auth"

# --- 1. AUTHENTIFICATION ---
if not st.session_state.logged_in:
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t2:
        with st.form("reg"):
            n, e, p = st.text_input("Nom"), st.text_input("Email"), st.text_input("Pass", type="password")
            if st.form_submit_button("S'inscrire"):
                if add_user(e, p, n): st.success("Compte créé !")
    with t1:
        el, pl = st.text_input("Email", key="l_e"), st.text_input("Pass", type="password", key="l_p")
        if st.button("Se connecter"):
            res = login_user(el, pl)
            if res:
                st.session_state.logged_in, st.session_state.user_name = True, res[0]
                st.session_state.page = "selection"
                st.rerun()
    st.stop()

# --- 2. SÉLECTION DES DOSSIERS ---
if st.session_state.page == "selection":
    st.title(f"📂 Dossiers de {st.session_state.user_name}")
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        if st.button("➕ Nouveau dossier", use_container_width=True):
            st.session_state.page = "cabinet"; st.rerun()
    with c2: st.button("🔄 En cours", use_container_width=True)
    with c3: st.button("⏳ À finaliser", use_container_width=True)
    with c4: st.button("✅ Terminés", use_container_width=True)
    st.stop()

# --- 3. CABINET (LES 11 ÉTAPES) ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user_name}")
    if st.button("⬅️ Retour aux dossiers"):
        st.session_state.page = "selection"; st.rerun()
    st.divider()
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", "5. Risques"]
    choice = st.radio("MÉTHODE FREEMAN", steps)
    idx = int(choice.split('.')[0])

col_l, col_r = st.columns([1, 1], gap="large")

with col_l:
    st.subheader(f"📍 {choice}")
    if idx == 1:
        faits = st.text_area("Exposez les faits précisément :", height=300)
        if st.button("🚀 ANALYSER AVEC KAREEM"):
            br, code, art, conseil = analyse_universelle_kareem(faits)
            st.session_state.last_analysis = {"br": br, "code": code, "art": art, "msg": conseil}
            st.rerun()

with col_r:
    st.subheader("🤖 Expertise de Kareem")
    if 'last_analysis' in st.session_state:
        ana = st.session_state.last_analysis
        st.metric("Domaine", ana['br'])
        st.metric("Source", ana['code'])
        typewriter(f"Analyse terminée. \n\nRéférence : **{ana['art']}**. \n\n{ana['msg']}")
