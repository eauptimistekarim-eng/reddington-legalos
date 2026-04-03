import streamlit as st
import sqlite3
import bcrypt
import time
from groq import Groq

# 1. CONFIGURATION
GROQ_KEY = "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"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS V2 - Freeman", layout="wide")

# 2. INITIALISATION BASE DE DONNÉES
def init_db():
    conn = sqlite3.connect('legalos_v2.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT, name TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS dossiers (nom TEXT, user_email TEXT, PRIMARY KEY(nom, user_email))')
    c.execute('CREATE TABLE IF NOT EXISTS steps (user_email TEXT, dossier_nom TEXT, step_idx INTEGER, faits TEXT, analyse TEXT, validated INTEGER DEFAULT 0, PRIMARY KEY(user_email, dossier_nom, step_idx))')
    conn.commit()
    conn.close()

init_db()

# 3. ÉTAT DE LA SESSION (CRUCIAL POUR LE BLOCAGE)
if "auth" not in st.session_state:
    st.session_state.auth = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "page" not in st.session_state:
    st.session_state.page = "cabinet"
if "current_step_idx" not in st.session_state:
    st.session_state.current_step_idx = 1

# 4. FONCTIONS AUTH
def check_login(e, p):
    try:
        conn = sqlite3.connect('legalos_v2.db')
        c = conn.cursor()
        c.execute("SELECT name, password FROM users WHERE email=?", (e,))
        res = c.fetchone()
        conn.close()
        if res:
            stored_pw = res[1].encode() if isinstance(res[1], str) else res[1]
            if bcrypt.checkpw(p.encode(), stored_pw):
                return res[0]
    except Exception as err:
        st.error(f"Erreur DB: {err}")
    return None

# 5. INTERFACE DE CONNEXION (SI NON AUTHENTIFIÉ)
if not st.session_state.auth:
    st.title("⚖️ LegalOS V2 - Accès Cabinet")
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    
    with t1:
        with st.form("form_login"):
            email_log = st.text_input("Email")
            pass_log = st.text_input("Mot de passe", type="password")
            btn_log = st.form_submit_button("Entrer")
            if btn_log:
                name = check_login(email_log, pass_log)
                if name:
                    st.session_state.auth = True
                    st.session_state.user_email = email_log
                    st.session_state.user_name = name
                    st.success(f"Bienvenue Me {name}")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Identifiants invalides")
    
    with t2:
        with st.form("form_reg"):
            n_reg = st.text_input("Nom complet")
            e_reg = st.text_input("Email")
            p_reg = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Créer le compte"):
                try:
                    conn = sqlite3.connect('legalos_v2.db')
                    c = conn.cursor()
                    h = bcrypt.hashpw(p_reg.encode(), bcrypt.gensalt()).decode()
                    c.execute("INSERT INTO users VALUES (?, ?, ?)", (e_reg, h, n_reg))
                    conn.commit()
                    conn.close()
                    st.success("Compte créé ! Connectez-vous sur l'autre onglet.")
                except:
                    st.error("Cet email existe déjà.")
    st.stop() # Arrête l'exécution ici si pas logué

# 6. LOGIQUE NAVIGATION APRÈS CONNEXION
if st.session_state.page == "cabinet":
    st.title(f"📂 Cabinet de Me {st.session_state.user_name}")
    
    col_a, col_b = st.columns([2, 1])
    with col_b:
        if st.button("➕ NOUVELLE AFFAIRE"):
            st.session_state.current_dossier = f"Affaire_{int(time.time())}"
            st.session_state.page = "work"
            st.rerun()
            
    with col_a:
        conn = sqlite3.connect('legalos_v2.db')
        c = conn.cursor()
        c.execute("SELECT nom FROM dossiers WHERE user_email=?", (st.session_state.user_email,))
        list_d = c.fetchall()
        conn.close()
        
        if not list_d:
            st.info("Aucun dossier en cours.")
        for d in list_d:
            if st.button(f"📁 {d[0]}", use_container_width=True):
                st.session_state.current_dossier = d[0]
                st.session_state.page = "work"
                st.rerun()

# 7. ZONE DE TRAVAIL (DÉROULÉ FREEMAN)
elif st.session_state.page == "work":
    steps = ["Qualification", "Objectif", "Base légale", "Inventaire", "Risques", "Amiable", "Stratégie", "Rédaction", "Audience", "Jugement", "Recours"]
    
    with st.sidebar:
        st.header("MÉTHODE FREEMAN")
        if st.button("⬅ Retour Cabinet"):
            st.session_state.page = "cabinet"
            st.rerun()
        
        # Navigation par étapes
        choice = st.radio("Étapes :", steps, index=st.session_state.current_step_idx - 1)
        st.session_state.current_step_idx = steps.index(choice) + 1
        idx = st.session_state.current_step_idx

    st.title(f"💼 {st.session_state.current_dossier}")
    st.subheader(f"Étape {idx} : {choice}")

    # Logique d'affichage et analyse (Kareem)...
    # [Le reste du code d'analyse suit la même logique que précédemment]
    st.write("Kareem est prêt pour l'analyse stratégique.")
