import streamlit as st
import time
from groq import Groq
from database import init_db, login_user, save_step_progress, get_full_history, get_user_dossiers

# --- INITIALISATION ---
init_db()
GROQ_KEY = "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"
STRIPE_LINK = "https://buy.stripe.com/9B6aEW6QF6Z6bFz3RY6c001"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS - Kareem IA", layout="wide")

# --- DESIGN STRICT ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .kareem-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; }
    .status-bar { background-color: #334155; height: 10px; border-radius: 5px; margin: 15px 0; overflow: hidden; }
    .status-fill { background: linear-gradient(90deg, #10b981, #3b82f6); height: 100%; border-radius: 5px; width: 40%; }
    .stMetric { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 10px !important; padding: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- EFFET MACHINE À ÉCRIRE ---
def typewriter(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold;">🤖 Kareem IA :</p>{full_text}▌</div>', unsafe_allow_html=True)
        time.sleep(0.005)
    container.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold;">🤖 Kareem IA :</p>{full_text}</div>', unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "selection"

# --- 1. CONNEXION ---
if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center;'>⚖️ Connexion LegalOS</h2>", unsafe_allow_html=True)
    with st.columns([1, 2, 1])[1]:
        with st.form("login"):
            e = st.text_input("Email")
            p = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Entrer"):
                res = login_user(e, p)
                if res:
                    st.session_state.auth, st.session_state.user_name, st.session_state.is_premium, st.session_state.user_email = True, res[0], res[1], e
                    st.rerun()
                else: st.error("Erreur d'identifiants.")
    st.stop()

# --- 2. CABINET ---
if st.session_state.page == "selection":
    st.title(f"📂 Cabinet de {st.session_state.user_name}")
    if st.button("➕ Nouveau Dossier"):
        st.session_state.current_dossier = "Affaire_" + str(int(time.time()))
        st.session_state.page = "cabinet"; st.rerun()
    st.divider()
    for d in get_user_dossiers(st.session_state.user_email):
        if st.button(f"📁 {d[0]} - {d[1]}", key=d[0]):
            st.session_state.current_dossier = d[0]
            st.session_state.page = "cabinet"; st.rerun()
    st.stop()

# --- 3. MÉTHODE FREEMAN (DISPOSITION) ---
with st.sidebar:
    st.title("MÉTHODE FREEMAN")
    if st.button("⬅️ Retour"): st.session_state.page = "selection"; st.rerun()
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", "5. Risques", "6. Stratégie"]
    choice = st.radio("Étape actuelle :", steps)
    idx = int(choice.split('.')[0])
    if not st.session_state.is_premium and idx > 3:
        st.link_button("🚀 PASSER PREMIUM", STRIPE_LINK)
        st.stop()

st.header(choice)
col_l, col_r = st.columns(2, gap="large")

with col_l:
    st.subheader(f"📝 {choice} du Dossier")
    with st.form("work_form"):
        faits = st.text_area("Décrivez les faits (incluez dates et montants) :", height=300)
        if st.form_submit_button("🚀 ANALYSE EXPERTE KAREEM"):
            _, hist = get_full_history(st.session_state.user_email, st.session_state.current_dossier)
            # IA comme un avocat : elle suit le contexte
            prompt = f"Historique : {hist}\nAction étape {idx} : Analyse ces faits : {faits}"
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Tu es Kareem, avocat expert. Suis l'affaire logiquement étape par étape."},
                          {"role": "user", "content": prompt}]
            )
            st.session_state.last_ia = resp.choices[0].message.content
            save_step_progress(st.session_state.user_email, st.session_state.current_dossier, faits, st.session_state.last_ia, idx)
            st.session_state.trigger_type = True
            st.rerun()

with col_r:
    st.subheader("🎯 Analyse de Kareem")
    c1, c2 = st.columns(2)
    c1.metric("Branche", "DROIT CIVIL")
    c2.metric("Chances de succès", f"{40 + idx*10}%")
    st.markdown('<div class="status-bar"><div class="status-fill"></div></div>', unsafe_allow_html=True)
    
    if 'last_ia' in st.session_state:
        if st.session_state.get('trigger_type', False):
            typewriter(st.session_state.last_ia)
            st.session_state.trigger_type = False
        else:
            st.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold;">🤖 Kareem :</p>{st.session_state.last_ia}</div>', unsafe_allow_html=True)
