import streamlit as st
import time
from groq import Groq
from database import *

# --- INITIALISATION ---
init_db()
client = Groq(api_key="TA_CLE_GROQ") # Remplace par ta clé

st.set_page_config(page_title="LegalOS - Méthode Freeman", layout="wide")

# --- STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .kareem-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; }
    .slogan { color: #94a3b8; font-style: italic; text-align: center; margin-bottom: 30px; font-size: 1.2em; }
    </style>
    """, unsafe_allow_html=True)

# --- PERSISTANCE SESSION ---
# On utilise les query_params pour "survivre" au refresh
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

# --- PAGE D'ACCUEIL / LOGIN ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>⚖️ LegalOS</h1>", unsafe_allow_html=True)
    st.markdown("<p class='slogan'>L'intelligence juridique au service de la Méthode Freeman.</p>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["Connexion", "Inscription", "Clé à usage unique"])
    with t1:
        with st.form("login"):
            e = st.text_input("Email")
            p = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Entrer dans le cabinet"):
                res = login_user(e, p)
                if res:
                    st.session_state.auth = True
                    st.session_state.user_name = res[0]
                    st.session_state.user_email = e
                    st.rerun()
    with t2:
        with st.form("reg"):
            n, e, p = st.text_input("Nom"), st.text_input("Email"), st.text_input("Pass", type="password")
            if st.form_submit_button("Créer compte"):
                if register_user(e, p, n): st.success("Ok ! Connectez-vous.")
    with t3:
        st.text_input("Clé unique")
        st.button("Activer")
    st.stop()

# --- CABINET DES DOSSIERS ---
if 'page' not in st.session_state: st.session_state.page = "cabinet"

if st.session_state.page == "cabinet":
    st.title(f"📂 Cabinet de {st.session_state.user_name}")
    if st.button("➕ Nouveau Dossier Freeman"):
        st.session_state.current_dossier = f"Affaire_{int(time.time())}"
        st.session_state.page = "travail"
        st.rerun()
    
    st.divider()
    dossiers = get_user_dossiers(st.session_state.user_email)
    for i, d_nom in enumerate(dossiers):
        # Utilisation d'un ID unique pour éviter DuplicateElementId
        if st.button(f"📁 {d_nom}", key=f"dossier_{i}_{d_nom}"):
            st.session_state.current_dossier = d_nom
            st.session_state.page = "travail"
            st.rerun()
    
    if st.sidebar.button("🚪 Déconnexion"):
        st.session_state.auth = False
        st.rerun()
    st.stop()

# --- ESPACE DE TRAVAIL : MÉTHODE FREEMAN ---
with st.sidebar:
    st.title("MÉTHODE FREEMAN")
    if st.button("⬅️ Retour au Cabinet"):
        st.session_state.page = "cabinet"
        st.rerun()
    
    steps = [
        "1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire",
        "5. Risques", "6. Amiable", "7. Stratégie", "8. Rédaction",
        "9. Audience", "10. Jugement", "11. Recours"
    ]
    choice = st.radio("Séquence :", steps)
    idx = int(choice.split('.')[0])

st.header(f"Dossier : {st.session_state.current_dossier}")

# Charger uniquement les données de CETTE étape
faits_etape, analyse_etape = get_step_specific_data(st.session_state.user_email, st.session_state.current_dossier, idx)

c1, c2 = st.columns(2, gap="large")

with c1:
    st.subheader(f"📝 Saisie : {choice}")
    with st.form(f"form_freeman_{idx}"):
        faits_in = st.text_area("Données de l'étape :", value=faits_etape, height=350)
        if st.form_submit_button("LANCER L'IA KAREEM"):
            # Kareem prend les choses en main : il reçoit TOUT le passé pour diriger le présent
            full_ctx = get_full_dossier_context(st.session_state.user_email, st.session_state.current_dossier)
            
            prompt = f"""Tu es Kareem, l'avocat en chef. Nous appliquons la MÉTHODE FREEMAN.
            HISTORIQUE DU DOSSIER : {full_ctx}
            ÉTAPE ACTUELLE : {choice}
            INPUT UTILISATEUR : {faits_in}
            
            MISSION : Ne sois pas un assistant, sois un leader. Analyse les faits, critique si nécessaire, 
            et donne l'instruction directe sur ce qu'il faut faire pour valider cette étape. 
            Si les faits sont insuffisants, réclame les preuves manquantes."""
            
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            res_text = resp.choices[0].message.content
            save_step_progress(st.session_state.user_email, st.session_state.current_dossier, faits_in, res_text, idx)
            st.session_state.last_ia = res_text
            st.session_state.trigger = True
            st.rerun()

with c2:
    st.subheader("🎯 Instruction Kareem")
    # Affichage intelligent
    ia_txt = st.session_state.get('last_ia', analyse_etape)
    if ia_txt:
        if st.session_state.get('trigger', False):
            typewriter(ia_txt)
            st.session_state.trigger = False
        else:
            st.markdown(f'<div class="kareem-card"><b>🤖 Kareem IA :</b><br>{ia_txt}</div>', unsafe_allow_html=True)
