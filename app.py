import streamlit as st
import time
from groq import Groq
from database import *

# --- INITIALISATION ---
init_db()
client = Groq(api_key="TA_CLE_API_GROQ") # Remplace par ta clé

st.set_page_config(page_title="LegalOS - Méthode Freeman", layout="wide")

# --- STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .kareem-card { background-color: #1e293b; padding: 25px; border-radius: 15px; border: 1px solid #334155; }
    .slogan { color: #94a3b8; font-style: italic; text-align: center; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# Persistence de la session
if 'auth' not in st.session_state:
    st.session_state.auth = False

def typewriter(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(f'<div class="kareem-card"><b style="color:#10b981;">🤖 Kareem IA :</b><br>{full_text}▌</div>', unsafe_allow_html=True)
        time.sleep(0.01)
    container.markdown(f'<div class="kareem-card"><b style="color:#10b981;">🤖 Kareem IA :</b><br>{text}</div>', unsafe_allow_html=True)

# --- LOGIN / INSCRIPTION ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>⚖️ LegalOS</h1>", unsafe_allow_html=True)
    st.markdown("<p class='slogan'>Maîtrisez votre dossier avec la Méthode Freeman.</p>", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["Connexion", "Créer un compte"])
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
            if st.form_submit_button("S'inscrire"):
                if register_user(e, p, n): st.success("Compte créé ! Connectez-vous.")
    st.stop()

# --- CABINET (SÉLECTION) ---
if 'page' not in st.session_state: st.session_state.page = "cabinet"

if st.session_state.page == "cabinet":
    st.title(f"📂 Cabinet de {st.session_state.user_name}")
    if st.button("➕ Nouveau Dossier Freeman"):
        st.session_state.current_dossier = f"Affaire_{int(time.time())}"
        st.session_state.page = "travail"; st.rerun()
    
    st.divider()
    dossiers = get_user_dossiers(st.session_state.user_email)
    for idx, d in enumerate(dossiers):
        # FIX : Ajout d'une clé unique pour éviter l'erreur DuplicateElementId
        if st.button(f"📁 {d[0]}", key=f"btn_{d[0]}_{idx}"):
            st.session_state.current_dossier = d[0]
            st.session_state.page = "travail"; st.rerun()
    
    if st.sidebar.button("🚪 Déconnexion"):
        st.session_state.auth = False; st.rerun()
    st.stop()

# --- MÉTHODE FREEMAN (TRAVAIL) ---
with st.sidebar:
    st.title("MÉTHODE FREEMAN")
    if st.button("⬅️ Menu Principal"): st.session_state.page = "cabinet"; st.rerun()
    
    steps = [f"{i+1}. {s}" for i, s in enumerate(["Qualification", "Objectif", "Base Légale", "Inventaire", "Risques", "Amiable", "Stratégie", "Rédaction", "Audience", "Jugement", "Recours"])]
    choice = st.radio("Progression :", steps)
    step_idx = int(choice.split('.')[0])

st.header(f"Dossier : {st.session_state.current_dossier}")

# Charger les données de l'étape choisie
faits_etape, analyse_etape = get_step_specific_data(st.session_state.user_email, st.session_state.current_dossier, step_idx)

col_l, col_r = st.columns(2, gap="large")

with col_l:
    st.subheader(f"📝 {choice}")
    with st.form(f"form_step_{step_idx}"):
        # Saisie indépendante
        faits_in = st.text_area("Notez vos éléments ou répondez à Kareem :", value=faits_etape, height=350)
        if st.form_submit_button("LANCER L'ANALYSE KAREEM"):
            ctx = get_full_dossier_context(st.session_state.user_email, st.session_state.current_dossier)
            
            # PROMPT : Kareem prend le lead
            prompt = f"""Tu es Kareem, l'avocat principal. On utilise la Méthode Freeman.
            CONTEXTE : {ctx}
            ÉTAPE : {choice}
            INPUT : {faits_in}
            MISSION : Prends le contrôle. Analyse si l'utilisateur fait fausse route. 
            Sois direct, exigeant sur les preuves et donne la marche à suivre immédiate."""
            
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            res_text = resp.choices[0].message.content
            save_step_progress(st.session_state.user_email, st.session_state.current_dossier, faits_in, res_text, step_idx)
            st.session_state.last_ia = res_text
            st.session_state.trigger = True
            st.rerun()

with col_r:
    st.subheader("🎯 Instructions de Kareem")
    ia_display = st.session_state.get('last_ia', analyse_etape)
    if ia_display:
        if st.session_state.get('trigger', False):
            typewriter(ia_display); st.session_state.trigger = False
        else:
            st.markdown(f'<div class="kareem-card"><b style="color:#10b981;">🤖 Kareem IA :</b><br>{ia_display}</div>', unsafe_allow_html=True)
