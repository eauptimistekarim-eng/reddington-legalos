import streamlit as st
import time
from groq import Groq
from database import init_db, login_user, register_user, save_step_progress, get_full_history, get_user_dossiers

# --- INITIALISATION ---
init_db()
GROQ_KEY = "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"
STRIPE_LINK = "https://buy.stripe.com/9B6aEW6QF6Z6bFz3RY6c001"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS - Kareem IA", layout="wide")

# --- DESIGN & SLOGAN ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .kareem-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; font-family: 'Courier New', monospace; }
    .slogan { color: #94a3b8; font-style: italic; font-size: 1.1em; margin-top: -20px; margin-bottom: 30px; text-align: center; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; justify-content: center; }
    </style>
    """, unsafe_allow_html=True)

def typewriter(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold;">🤖 Kareem IA :</p>{full_text}▌</div>', unsafe_allow_html=True)
        time.sleep(0.01)
    container.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold;">🤖 Kareem IA :</p>{text}</div>', unsafe_allow_html=True)

# --- AUTHENTIFICATION (Tabs) ---
if 'auth' not in st.session_state:
    st.markdown("<h1 style='text-align:center;'>⚖️ LegalOS</h1>", unsafe_allow_html=True)
    st.markdown("<p class='slogan'>L'intelligence juridique au service de la méthode Reddington.</p>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["Connexion", "Inscription", "Clé à usage unique"])
    
    with t1:
        with st.form("login"):
            e, p = st.text_input("Email"), st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Entrer"):
                res = login_user(e, p)
                if res:
                    st.session_state.auth, st.session_state.user_name, st.session_state.is_premium, st.session_state.user_email = True, res[0], res[1], e
                    st.rerun()
                else: st.error("Identifiants incorrects.")
    with t2:
        with st.form("register"):
            n, e, p = st.text_input("Nom complet"), st.text_input("Email"), st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Créer un compte"):
                if register_user(e, p, n): st.success("Compte créé ! Connectez-vous.")
                else: st.error("Email déjà utilisé.")
    with t3:
        st.text_input("Entrez votre clé")
        st.button("Vérifier la clé")
    st.stop()

# --- CABINET & MÉMOIRE ---
if 'page' not in st.session_state: st.session_state.page = "selection"

if st.session_state.page == "selection":
    st.title(f"📂 Cabinet de {st.session_state.user_name}")
    if st.button("➕ Nouveau Dossier"):
        st.session_state.current_dossier = f"Affaire_{int(time.time())}"
        st.session_state.page = "cabinet"; st.session_state.last_ia = ""; st.rerun()
    
    st.divider()
    for d in get_user_dossiers(st.session_state.user_email):
        if st.button(f"📁 {d[0]} (Reprendre à l'étape {d[1]})"):
            st.session_state.current_dossier = d[0]
            # ON CHARGE LA MÉMOIRE ICI
            faits, hist = get_full_history(st.session_state.user_email, d[0])
            st.session_state.last_ia = hist.split('---')[-1].strip() if hist else ""
            st.session_state.page = "cabinet"; st.rerun()
    st.stop()

# --- MÉTHODE REDDINGTON (11 ÉTAPES) ---
with st.sidebar:
    st.title("MÉTHODE REDDINGTON")
    if st.button("⬅️ Menu Principal"): st.session_state.page = "selection"; st.rerun()
    steps = [f"{i+1}. {s}" for i, s in enumerate(["Qualification", "Objectif", "Base Légale", "Inventaire", "Risques", "Amiable", "Stratégie", "Rédaction", "Audience", "Jugement", "Recours"])]
    choice = st.radio("Navigation :", steps)
    idx = int(choice.split('.')[0])
    if not st.session_state.is_premium and idx > 3:
        st.warning("🔒 Section Premium")
        st.link_button("🚀 Débloquer", STRIPE_LINK)
        st.stop()

# --- INTERFACE TRAVAIL ---
st.header(f"Dossier : {st.session_state.current_dossier} - {choice}")
col_l, col_r = st.columns(2, gap="large")

with col_l:
    st.subheader("📝 Saisie des informations")
    faits_anciens, _ = get_full_history(st.session_state.user_email, st.session_state.current_dossier)
    with st.form("work_form"):
        faits_in = st.text_area("Précisez les éléments de cette étape :", value=faits_anciens, height=350)
        if st.form_submit_button("🛠️ ANALYSE KAREEM"):
            _, hist = get_full_history(st.session_state.user_email, st.session_state.current_dossier)
            prompt = f"Historique : {hist}\nÉtape : {choice}\nNouveaux faits : {faits_in}\nMission : Agis comme un avocat expert."
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Tu es Kareem, avocat expert utilisant la méthode Reddington."},
                          {"role": "user", "content": prompt}]
            )
            st.session_state.last_ia = resp.choices[0].message.content
            save_step_progress(st.session_state.user_email, st.session_state.current_dossier, faits_in, st.session_state.last_ia, idx)
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
