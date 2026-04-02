import streamlit as st
import time
from groq import Groq
from database import *

init_db()
GROQ_KEY = "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"
STRIPE_LINK = "https://buy.stripe.com/9B6aEW6QF6Z6bFz3RY6c001"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS - Kareem IA", layout="wide")

# --- STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .kareem-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; font-family: 'Courier New', monospace; }
    .slogan { color: #94a3b8; font-style: italic; margin-bottom: 30px; }
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

# --- AUTHENTIFICATION ---
if 'auth' not in st.session_state:
    st.title("⚖️ LegalOS")
    st.markdown("<p class='slogan'>L'intelligence juridique au service de la méthode Freeman.</p>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Connexion", "Inscription", "Clé unique"])
    
    with tab1:
        with st.form("login"):
            e, p = st.text_input("Email"), st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Se connecter"):
                res = login_user(e, p)
                if res:
                    st.session_state.auth, st.session_state.user_name, st.session_state.is_premium, st.session_state.user_email = True, res[0], res[1], e
                    st.rerun()
    with tab2:
        with st.form("reg"):
            n, e, p = st.text_input("Nom"), st.text_input("Email"), st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Créer un compte"):
                if register_user(e, p, n): st.success("Compte créé ! Connectez-vous.")
    with tab3:
        st.text_input("Entrez votre clé d'accès temporaire")
        st.button("Vérifier la clé")
    st.stop()

# --- CABINET ---
if 'page' not in st.session_state: st.session_state.page = "selection"

if st.session_state.page == "selection":
    st.title(f"📂 Cabinet de {st.session_state.user_name}")
    if st.button("➕ Nouveau Dossier"):
        st.session_state.current_dossier = f"Dossier_{int(time.time())}"
        st.session_state.page = "cabinet"; st.rerun()
    st.divider()
    for d in get_user_dossiers(st.session_state.user_email):
        if st.button(f"📁 {d[0]} (Étape {d[1]})"):
            st.session_state.current_dossier = d[0]
            st.session_state.page = "cabinet"; st.rerun()
    st.stop()

# --- MÉTHODE REDDINGTON (11 ÉTAPES) ---
with st.sidebar:
    st.title("MÉTHODE REDDINGTON")
    if st.button("⬅️ Menu Principal"): st.session_state.page = "selection"; st.rerun()
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", "5. Risques", 
             "6. Amiable", "7. Stratégie", "8. Rédaction", "9. Audience", "10. Jugement", "11. Recours"]
    choice = st.radio("Navigation :", steps)
    idx = int(choice.split('.')[0])
    if not st.session_state.is_premium and idx > 3:
        st.warning("🔒 Section Premium")
        st.link_button("🚀 Débloquer LegalOS", STRIPE_LINK)
        st.stop()

# --- INTERFACE TRAVAIL ---
st.header(choice)
col_l, col_r = st.columns(2, gap="large")

with col_l:
    st.subheader("📝 Faits & Données")
    with st.form("avocat_form"):
        faits = st.text_area("Remplissez les éléments requis pour cette étape :", height=350)
        if st.form_submit_button("🛠️ GÉNÉRER ANALYSE KAREEM"):
            _, hist = get_full_history(st.session_state.user_email, st.session_state.current_dossier)
            prompt = f"Historique du dossier : {hist}\nÉtape actuelle : {choice}\nNouveaux faits : {faits}\nMission : En tant que Kareem, agis comme un avocat et complète cette étape."
            
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Tu es Kareem. Tu es un avocat expert utilisant la méthode Freeman."},
                          {"role": "user", "content": prompt}]
            )
            st.session_state.ia_out = resp.choices[0].message.content
            save_step_progress(st.session_state.user_email, st.session_state.current_dossier, faits, st.session_state.ia_out, idx)
            st.session_state.trigger = True
            st.rerun()

with col_r:
    st.subheader("🎯 Conseil de Kareem")
    if 'ia_out' in st.session_state:
        if st.session_state.get('trigger', False):
            typewriter(st.session_state.ia_out)
            st.session_state.trigger = False
        else:
            st.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold;">🤖 Kareem IA :</p>{st.session_state.ia_out}</div>', unsafe_allow_html=True)
