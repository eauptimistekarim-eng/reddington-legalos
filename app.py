import streamlit as st
import time
from groq import Groq
from database import * # Importation propre pour éviter NameError

# --- SETUP ---
init_db()
client = Groq(api_key="TA_CLE_GROQ_ICI") # À remplacer
st.set_page_config(page_title="LegalOS - Méthode Freeman", layout="wide")

# --- STYLE & PERSISTANCE ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .kareem-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; }
    .slogan { color: #94a3b8; font-style: italic; text-align: center; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# Gestion de la persistence (Survit au refresh tant que l'onglet est ouvert)
if 'auth' not in st.session_state:
    st.session_state.auth = False

def typewriter(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(f'<div class="kareem-card"><b>🤖 Kareem IA :</b><br>{full_text}▌</div>', unsafe_allow_html=True)
        time.sleep(0.01)
    container.markdown(f'<div class="kareem-card"><b>🤖 Kareem IA :</b><br>{text}</div>', unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>⚖️ LegalOS</h1>", unsafe_allow_html=True)
    st.markdown("<p class='slogan'>Expertise juridique via la Méthode Freeman.</p>", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        with st.form("login"):
            e, p = st.text_input("Email"), st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Entrer"):
                res = login_user(e, p)
                if res:
                    st.session_state.auth, st.session_state.user_name, st.session_state.user_email = True, res[0], e
                    st.rerun()
    with t2:
        with st.form("reg"):
            n, e, p = st.text_input("Nom"), st.text_input("Email"), st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Créer compte"):
                if register_user(e, p, n): st.success("Compte créé !")
    st.stop()

# --- CABINET ---
if 'page' not in st.session_state: st.session_state.page = "cabinet"

if st.session_state.page == "cabinet":
    st.title(f"📂 Cabinet de {st.session_state.user_name}")
    if st.button("➕ Nouveau Dossier Freeman"):
        st.session_state.current_dossier = f"Dossier_{int(time.time())}"
        st.session_state.page = "travail"; st.rerun()
    
    for d in get_user_dossiers(st.session_state.user_email):
        if st.button(f"📁 {d[0]}"):
            st.session_state.current_dossier = d[0]
            st.session_state.page = "travail"; st.rerun()
    
    if st.sidebar.button("🚪 Déconnexion"):
        st.session_state.auth = False; st.rerun()
    st.stop()

# --- MÉTHODE FREEMAN (ZONE DE TRAVAIL) ---
with st.sidebar:
    st.title("MÉTHODE FREEMAN")
    if st.button("⬅️ Retour Cabinet"): st.session_state.page = "cabinet"; st.rerun()
    
    steps = [f"{i+1}. {s}" for i, s in enumerate(["Qualification", "Objectif", "Base Légale", "Inventaire", "Risques", "Amiable", "Stratégie", "Rédaction", "Audience", "Jugement", "Recours"])]
    choice = st.radio("Progression :", steps)
    idx = int(choice.split('.')[0])

st.header(f"Dossier : {st.session_state.current_dossier}")
faits_etape, analyse_etape = get_step_specific_data(st.session_state.user_email, st.session_state.current_dossier, idx)

col_l, col_r = st.columns(2)

with col_l:
    st.subheader(f"📝 {choice}")
    with st.form(f"form_{idx}"):
        faits_in = st.text_area("Saisissez vos notes ou répondez à Kareem :", value=faits_etape, height=300)
        if st.form_submit_button("LANCER L'ANALYSE FREEMAN"):
            # Kareem prend les choses en main ici via le prompt
            ctx = get_full_dossier_context(st.session_state.user_email, st.session_state.current_dossier)
            prompt = f"""Tu es Kareem, l'avocat en chef. Tu diriges le dossier selon la Méthode Freeman.
            CONTEXTE ACTUEL : {ctx}
            ÉTAPE ACTUELLE : {choice}
            INPUT UTILISATEUR : {faits_in}
            MISSION : Prends le dossier en main. Analyse, critique, et dis précisément à l'utilisateur ce qu'il doit faire ensuite ou quelles preuves il doit apporter. Ne sois pas passif."""
            
            resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            res_text = resp.choices[0].message.content
            save_step_progress(st.session_state.user_email, st.session_state.current_dossier, faits_in, res_text, idx)
            st.session_state.last_ia = res_text
            st.session_state.trigger = True
            st.rerun()

with col_r:
    st.subheader("🎯 Direction Kareem")
    txt = st.session_state.get('last_ia', analyse_etape)
    if txt:
        if st.session_state.get('trigger', False):
            typewriter(txt); st.session_state.trigger = False
        else:
            st.markdown(f'<div class="kareem-card"><b>🤖 Kareem IA :</b><br>{txt}</div>', unsafe_allow_html=True)
