import streamlit as st
import time
from groq import Groq
from database import init_db, login_user, save_dossier, get_user_dossiers

init_db()
GROQ_KEY = "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"
STRIPE_LINK = "https://buy.stripe.com/9B6aEW6QF6Z6bFz3RY6c001"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS - Kareem IA", layout="wide")

# --- DESIGN STRICT (Inchangé) ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .kareem-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; min-height: 200px; }
    .status-bar { background-color: #334155; height: 10px; border-radius: 5px; margin: 15px 0; }
    .status-fill { background: linear-gradient(90deg, #10b981, #3b82f6); height: 100%; border-radius: 5px; width: 85%; }
    </style>
    """, unsafe_allow_html=True)

# --- EFFET MACHINE À ÉCRIRE ---
def typewriter(text):
    container = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        container.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold;">🤖 Kareem IA :</p>{displayed}▌</div>', unsafe_allow_html=True)
        time.sleep(0.01)
    container.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold;">🤖 Kareem IA :</p>{displayed}</div>', unsafe_allow_html=True)

# --- NAVIGATION & AUTH ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "selection"

if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center;'>⚖️ Accès LegalOS</h2>", unsafe_allow_html=True)
    with st.form("login"):
        e, p = st.text_input("Email"), st.text_input("Pass", type="password")
        if st.form_submit_button("Entrer"):
            res = login_user(e, p)
            if res:
                st.session_state.auth, st.session_state.user_name, st.session_state.is_premium, st.session_state.user_email = True, res[0], res[1], e
                st.rerun()
    st.stop()

# --- CABINET ---
if st.session_state.page == "selection":
    st.title(f"📂 Dossiers de {st.session_state.user_name}")
    if st.button("➕ Nouveau Dossier"): st.session_state.page = "cabinet"; st.rerun()
    dossiers = get_user_dossiers(st.session_state.user_email)
    for d in dossiers:
        with st.expander(f"📁 {d[0]}"):
            if st.button(f"Ouvrir {d[0]}", key=d[0]): st.session_state.page = "cabinet"; st.rerun()
    st.stop()

# --- MÉTHODE FREEMAN PROGRESSIVE ---
with st.sidebar:
    st.title("MÉTHODE FREEMAN")
    if st.button("⬅️ Menu"): st.session_state.page = "selection"; st.rerun()
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", "5. Risques", "6. Stratégie", "7. Rédaction"]
    choice = st.radio("Étape actuelle :", steps)
    idx = int(choice.split('.')[0])
    if not st.session_state.is_premium: st.link_button("🚀 PREMIUM", STRIPE_LINK)

if idx > 3 and not st.session_state.is_premium:
    st.error("🔒 Étape Premium. Veuillez vous abonner.")
    st.stop()

# --- INTERFACE 2 COLONNES ---
st.header(choice)
col_l, col_r = st.columns(2, gap="large")

with col_l:
    st.subheader("📝 Action Utilisateur")
    with st.form("f_form"):
        nom_d = st.text_input("Nom du dossier", value="Affaire X")
        faits = st.text_area("Faits et contexte :", height=250)
        
        # Instruction dynamique selon l'étape
        prompts = {
            1: "Analyse la branche du droit et qualifie juridiquement ces faits.",
            2: "Détermine l'objectif juridique optimal (dommages, annulation, etc.) pour ce cas.",
            3: "Cite les articles précis du Code Civil ou Pénal applicables ici.",
            4: "Fais l'inventaire des preuves nécessaires pour gagner ce dossier."
        }
        
        if st.form_submit_button("Lancer l'Analyse"):
            with st.spinner("Kareem réfléchit..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": f"Tu es Kareem. Étape actuelle : {choice}. {prompts.get(idx, 'Analyse le dossier.')}"},
                              {"role": "user", "content": faits}]
                )
                st.session_state.last_res = response.choices[0].message.content
                save_dossier(st.session_state.user_email, nom_d, faits, choice)
                st.session_state.trigger_typewriter = True

with col_r:
    st.subheader("🎯 Intelligence Kareem")
    st.metric("Fiabilité de l'analyse", f"{70 + idx*5}%")
    st.markdown('<div class="status-bar"><div class="status-fill"></div></div>', unsafe_allow_html=True)
    
    if 'last_res' in st.session_state:
        if st.session_state.get('trigger_typewriter', False):
            typewriter(st.session_state.last_res)
            st.session_state.trigger_typewriter = False
        else:
            st.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold;">🤖 Kareem IA :</p>{st.session_state.last_res}</div>', unsafe_allow_html=True)
