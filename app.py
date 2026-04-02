import streamlit as st
import time
from groq import Groq
from database import *

init_db()
GROQ_KEY = "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"
STRIPE_LINK = "https://buy.stripe.com/9B6aEW6QF6Z6bFz3RY6c001"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS - Kareem IA", layout="wide")

# --- DESIGN FIGÉ (Identique aux captures) ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .kareem-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; }
    .status-bar { background-color: #334155; height: 10px; border-radius: 5px; margin: 15px 0; overflow: hidden; }
    .status-fill { background: linear-gradient(90deg, #10b981, #3b82f6); height: 100%; border-radius: 5px; width: 85%; }
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

# --- NAVIGATION ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    # (Composant Login ici - omit pour brièveté, identique au précédent)
    st.stop()

with st.sidebar:
    st.title("⚖️ LegalOS")
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", "5. Risques", "6. Stratégie", "7. Rédaction"]
    choice = st.radio("Progression du dossier :", steps)
    idx = int(choice.split('.')[0])
    if not st.session_state.is_premium and idx > 3:
        st.warning("🔒 Premium requis")
        st.link_button("S'abonner", STRIPE_LINK)
        st.stop()

# --- LOGIQUE PROGRESSIVE ---
st.title(choice)
col_l, col_r = st.columns(2, gap="large")

with col_l:
    st.subheader("📝 Éléments du dossier")
    with st.form("progress_form"):
        nom_d = st.text_input("Dossier actuel", value="Affaire Freeman")
        faits = st.text_area("Nouveaux faits ou précisions :", height=250)
        
        if st.form_submit_button("🔨 Faire progresser l'affaire"):
            # On récupère tout ce qu'on sait déjà
            faits_anciens, historique = get_full_history(st.session_state.user_email, nom_d)
            
            # Instructions spécifiques pour simuler un avocat
            instructions = {
                1: "Analyse les faits et donne la qualification juridique exacte.",
                2: f"Basé sur la qualification précédente ({historique}), quel est l'objectif judiciaire ?",
                3: f"Cite les articles de loi précis pour soutenir l'objectif identifié.",
                4: "Quelles preuves l'utilisateur doit-il fournir pour gagner ?",
            }
            
            prompt_final = f"Historique du dossier : {historique}\nNouveaux éléments : {faits}\nMission : {instructions.get(idx)}"
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Tu es Kareem, un avocat rigoureux. Tu construis ton dossier étape par étape."},
                          {"role": "user", "content": prompt_final}]
            )
            
            res_ia = response.choices[0].message.content
            save_step_progress(st.session_state.user_email, nom_d, faits, res_ia, idx)
            st.session_state.last_res = res_ia
            st.session_state.show_typewriter = True
            st.rerun()

with col_r:
    st.subheader("🎯 Stratégie Kareem")
    st.metric("Solidité du dossier", f"{60 + idx*5}%")
    st.markdown('<div class="status-bar"><div class="status-fill"></div></div>', unsafe_allow_html=True)
    
    if 'last_res' in st.session_state:
        if st.session_state.get('show_typewriter', False):
            typewriter(st.session_state.last_res)
            st.session_state.show_typewriter = False
        else:
            st.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold;">🤖 Kareem IA :</p>{st.session_state.last_res}</div>', unsafe_allow_html=True)
