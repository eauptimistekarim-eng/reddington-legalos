import streamlit as st
import time
from groq import Groq
from database import *

init_db()
GROQ_KEY = "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"
STRIPE_LINK = "https://buy.stripe.com/9B6aEW6QF6Z6bFz3RY6c001"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS - Kareem IA", layout="wide")

# --- DESIGN (Slogan & Squelette) ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .kareem-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; font-family: 'Courier New', monospace; }
    .slogan { color: #94a3b8; font-style: italic; font-size: 0.9em; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

def typewriter(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold;">🤖 Kareem IA :</p>{full_text}▌</div>', unsafe_allow_html=True)
        time.sleep(0.01)
    container.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold;">🤖 Kareem IA :</p>{full_text}</div>', unsafe_allow_html=True)

# --- GESTION DE LA PERSISTENCE (Le correctif) ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("⚖️ LegalOS")
    st.markdown("<p class='slogan'>L'intelligence juridique au service de la méthode Reddington.</p>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Connexion", "Inscription", "Clé unique"])
    with tab1:
        with st.form("login"):
            e, p = st.text_input("Email"), st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Se connecter"):
                res = login_user(e, p)
                if res:
                    st.session_state.auth, st.session_state.user_name, st.session_state.is_premium, st.session_state.user_email = True, res[0], res[1], e
                    st.rerun()
    # ... (Garder tab2 et tab3 comme avant)
    st.stop()

# --- SI CONNECTÉ : CHARGEMENT DES DONNÉES ---
if 'page' not in st.session_state: st.session_state.page = "selection"

if st.session_state.page == "selection":
    st.title(f"📂 Cabinet de {st.session_state.user_name}")
    if st.button("➕ Nouveau Dossier"):
        st.session_state.current_dossier = f"Dossier_{int(time.time())}"
        st.session_state.page = "cabinet"
        st.session_state.last_ia = "" # Reset pour nouveau dossier
        st.rerun()
    
    st.divider()
    dossiers = get_user_dossiers(st.session_state.user_email)
    for d in dossiers:
        if st.button(f"📁 {d[0]} (Reprendre)"):
            st.session_state.current_dossier = d[0]
            # ON RECHARGE L'HISTORIQUE DEPUIS LA DB ICI
            faits, hist = get_full_history(st.session_state.user_email, d[0])
            st.session_state.last_ia = hist.split('\n')[-2] if hist else "" # On récupère la dernière parole
            st.session_state.page = "cabinet"
            st.rerun()
    st.stop()

# --- MODE TRAVAIL (11 ÉTAPES) ---
with st.sidebar:
    st.title("MÉTHODE REDDINGTON")
    if st.button("⬅️ Menu Principal"): st.session_state.page = "selection"; st.rerun()
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", "5. Risques", "6. Amiable", "7. Stratégie", "8. Rédaction", "9. Audience", "10. Jugement", "11. Recours"]
    choice = st.radio("Étape :", steps)
    idx = int(choice.split('.')[0])

# --- INTERFACE ---
st.header(f"Dossier : {st.session_state.current_dossier} - {choice}")
col_l, col_r = st.columns(2, gap="large")

with col_l:
    st.subheader("📝 Faits & Données")
    # On affiche les faits déjà enregistrés si présents
    faits_ancients, _ = get_full_history(st.session_state.user_email, st.session_state.current_dossier)
    with st.form("avocat_form"):
        faits_input = st.text_area("Remplissez les éléments :", value=faits_ancients, height=350)
        if st.form_submit_button("🛠️ ANALYSE KAREEM"):
            _, hist = get_full_history(st.session_state.user_email, st.session_state.current_dossier)
            prompt = f"Historique : {hist}\nÉtape : {choice}\nAction : {faits_input}"
            
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Tu es Kareem, avocat expert."},
                          {"role": "user", "content": prompt}]
            )
            st.session_state.last_ia = resp.choices[0].message.content
            save_step_progress(st.session_state.user_email, st.session_state.current_dossier, faits_input, st.session_state.last_ia, idx)
            st.session_state.trigger = True
            st.rerun()

with col_r:
    st.subheader("🎯 Conseil de Kareem")
    if 'last_ia' in st.session_state and st.session_state.last_ia:
        if st.session_state.get('trigger', False):
            typewriter(st.session_state.last_ia)
            st.session_state.trigger = False
        else:
            st.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold;">🤖 Kareem IA :</p>{st.session_state.last_ia}</div>', unsafe_allow_html=True)
