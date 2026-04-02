import streamlit as st
import time
from groq import Groq
from database import *

# --- CONFIGURATION ---
init_db()
client = Groq(api_key="VOTRE_CLE_GROQ")
STRIPE_LINK = "https://buy.stripe.com/9B6aEW6QF6Z6bFz3RY6c001"

st.set_page_config(page_title="LegalOS - Kareem IA", layout="wide")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .kareem-box { background-color: #161e2e; padding: 20px; border-radius: 12px; border-left: 4px solid #10b981; color: #10b981; border: 1px solid #1e293b; }
    .premium-lock { background-color: #450a0a; padding: 20px; border-radius: 12px; border: 1px solid #ef4444; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "selection"

# --- 1. AUTHENTIFICATION (ENTRÉE ACTIVE) ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center; color:#10b981;'>⚖️ LegalOS Access</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        with st.form("login"):
            e = st.text_input("Email")
            p = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Entrer"):
                res = login_user(e, p)
                if res:
                    st.session_state.auth, st.session_state.user_name, st.session_state.is_premium, st.session_state.user_email = True, res[0], res[1], e
                    st.rerun()
    with t2:
        with st.form("signup"):
            nn, ne, np = st.text_input("Nom"), st.text_input("Email"), st.text_input("Pass", type="password")
            if st.form_submit_button("S'inscrire"):
                if add_user(ne, np, nn): st.success("Compte créé ! Mail envoyé.")
    st.stop()

# --- 2. CABINET DE DOSSIERS ---
if st.session_state.page == "selection":
    st.title(f"📂 Cabinet de {st.session_state.user_name}")
    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("➕ Nouveau Dossier", use_container_width=True):
            st.session_state.page = "cabinet"; st.rerun()
    with c2:
        dossiers = get_user_dossiers(st.session_state.user_email)
        for d in dossiers:
            with st.expander(f"📁 {d[0]} ({d[1]})"):
                st.write(d[3])
                if st.button(f"Ouvrir {d[0]}", key=d[0]):
                    st.session_state.page = "cabinet"; st.rerun()
    st.stop()

# --- 3. MÉTHODE FREEMAN (11 ÉTAPES) ---
with st.sidebar:
    st.title("⚖️ LegalOS")
    if st.button("⬅️ Menu Principal"): st.session_state.page = "selection"; st.rerun()
    st.divider()
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", "5. Risques", "6. Amiable", "7. Stratégie", "8. Rédaction", "9. Audience", "10. Jugement", "11. Recours"]
    choice = st.radio("MÉTHODE FREEMAN", steps)
    idx = int(choice.split('.')[0])
    
    if not st.session_state.is_premium:
        st.info("🔓 Mode Démo (Étapes 1-3)")
        st.link_button("🚀 PASSER PREMIUM", STRIPE_LINK)

# --- LOGIQUE DE VERROUILLAGE ---
if idx > 3 and not st.session_state.is_premium:
    st.markdown(f"""
    <div class="premium-lock">
        <h2>🔒 Étape {choice} Verrouillée</h2>
        <p>L'analyse stratégique et la rédaction automatique sont réservées aux membres Premium.</p>
        <a href="{STRIPE_LINK}" target="_blank" style="color:white; font-weight:bold; text-decoration:none; background:#ef4444; padding:10px 20px; border-radius:5px; display:inline-block; margin-top:10px;">DÉBLOQUER MAINTENANT</a>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- CONTENU DES ÉTAPES ---
st.title(choice)
col_l, col_r = st.columns(2, gap="large")

with col_l:
    if idx == 1:
        with st.form("step1"):
            nom_d = st.text_input("Nom du dossier")
            faits = st.text_area("Exposez les faits :", height=250)
            if st.form_submit_button("Analyse Kareem"):
                with st.spinner("Kareem analyse..."):
                    chat = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "Tu es Kareem, expert juridique. Analyse la branche du droit et l'article applicable."},
                                  {"role": "user", "content": faits}]
                    )
                    st.session_state.k_resp = chat.choices[0].message.content
                    save_dossier(st.session_state.user_email, nom_d, faits, "Analyse Complétée")
                    st.rerun()
    else:
        st.info(f"Contenu de l'étape {idx} en cours de développement...")

with col_r:
    st.subheader("🤖 Kareem IA")
    if 'k_resp' in st.session_state:
        st.markdown(f'<div class="kareem-box">{st.session_state.k_resp}</div>', unsafe_allow_html=True)
