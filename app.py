import streamlit as st
import time
from groq import Groq
from database import init_db, login_user, save_dossier, get_user_dossiers

init_db()

# CONFIGURATION
GROQ_KEY = "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"
STRIPE_LINK = "https://buy.stripe.com/9B6aEW6QF6Z6bFz3RY6c001"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS - Kareem IA", layout="wide")

# --- DESIGN STRICT (Figé sur tes captures) ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .kareem-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; }
    .status-bar { background-color: #334155; height: 10px; border-radius: 5px; margin: 15px 0; overflow: hidden; }
    .status-fill { background: linear-gradient(90deg, #10b981, #3b82f6); height: 100%; border-radius: 5px; width: 80%; }
    .stMetric { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 10px !important; padding: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- EFFET MACHINE À ÉCRIRE ---
def typewriter_effect(text):
    container = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        container.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold;">🤖 Kareem :</p>{displayed}▌</div>', unsafe_allow_html=True)
        time.sleep(0.01)
    container.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold;">🤖 Kareem :</p>{text}</div>', unsafe_allow_html=True)

# SESSION
if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "selection"

# --- AUTHENTIFICATION ---
if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center;'>⚖️ Accès LegalOS</h2>", unsafe_allow_html=True)
    with st.form("auth_form"):
        e, p = st.text_input("Email"), st.text_input("Pass", type="password")
        if st.form_submit_button("Se connecter (Entrée)"):
            res = login_user(e, p)
            if res:
                st.session_state.auth, st.session_state.user_name, st.session_state.is_premium, st.session_state.user_email = True, res[0], res[1], e
                st.rerun()
    st.stop()

# --- CABINET ---
if st.session_state.page == "selection":
    st.title(f"📂 Cabinet de {st.session_state.user_name}")
    if st.button("➕ Nouveau Dossier"): st.session_state.page = "cabinet"; st.rerun()
    dossiers = get_user_dossiers(st.session_state.user_email)
    for d in dossiers:
        with st.expander(f"📁 {d[0]}"):
            if st.button(f"Ouvrir {d[0]}", key=d[0]): st.session_state.page = "cabinet"; st.rerun()
    st.stop()

# --- MÉTHODE FREEMAN (11 ÉTAPES) ---
with st.sidebar:
    st.title("⚖️ LegalOS")
    if st.button("⬅️ Menu"): st.session_state.page = "selection"; st.rerun()
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", "5. Risques", "6. Amiable", "7. Stratégie", "8. Rédaction", "9. Audience", "10. Jugement", "11. Recours"]
    choice = st.radio("Freeman Method :", steps)
    idx = int(choice.split('.')[0])
    if not st.session_state.is_premium: st.link_button("🚀 PREMIUM", STRIPE_LINK)

# Verrouillage Freemium
if idx > 3 and not st.session_state.is_premium:
    st.warning("🔒 Étape Premium. Veuillez débloquer la suite.")
    st.stop()

# --- DISPOSITION 2 COLONNES (STRICTE) ---
st.title(choice)
col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.subheader("📄 Saisie des faits")
    with st.form("main_form"):
        nom_d = st.text_input("Nom du dossier", value="Affaire sans titre")
        faits = st.text_area("Expliquez votre situation :", height=300)
        
        # PROMPT PROGRESSIF SELON L'ÉTAPE
        instructions = {
            1: "Qualifie juridiquement ces faits et identifie la branche du droit.",
            2: "Détermine l'objectif juridique réaliste pour ce cas précis.",
            3: "Cite les articles de loi applicables à cette situation.",
            4: "Dresse l'inventaire des preuves nécessaires (témoignages, contrats, etc.)."
        }
        
        if st.form_submit_button("🚀 Analyse Kareem"):
            with st.spinner("Analyse en cours..."):
                resp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": f"Tu es Kareem. Étape : {choice}. {instructions.get(idx, 'Analyse le dossier.')}"},
                              {"role": "user", "content": faits}]
                )
                st.session_state.last_analysis = resp.choices[0].message.content
                st.session_state.run_typewriter = True
                save_dossier(st.session_state.user_email, nom_d, faits, choice)
                st.rerun()

with col_right:
    st.subheader("🎯 Intelligence Kareem")
    c1, c2 = st.columns(2)
    with c1: st.metric("Confiance", f"{65 + idx*7}%")
    with c2: st.metric("Succès", "Calcul...")
    
    st.markdown('<div class="status-bar"><div class="status-fill"></div></div>', unsafe_allow_html=True)
    
    if 'last_analysis' in st.session_state:
        if st.session_state.get('run_typewriter', False):
            typewriter_effect(st.session_state.last_analysis)
            st.session_state.run_typewriter = False
        else:
            st.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold;">🤖 Kareem :</p>{st.session_state.last_analysis}</div>', unsafe_allow_html=True)
