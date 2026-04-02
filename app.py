import streamlit as st
import time
from groq import Groq
from database import init_db, login_user, save_dossier, get_user_dossiers

init_db()
client = Groq(api_key="VOTRE_CLE_GROQ")
STRIPE_LINK = "https://buy.stripe.com/9B6aEW6QF6Z6bFz3RY6c001"

st.set_page_config(page_title="LegalOS - Kareem IA", layout="wide")

# --- DESIGN STRICT (Garder la disposition et le design) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0f172a; color: #f8fafc; }}
    .kareem-card {{ background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; }}
    .status-bar {{ background-color: #1e293b; height: 8px; border-radius: 4px; margin: 10px 0; }}
    .status-fill {{ background: linear-gradient(90deg, #3b82f6, #10b981); height: 100%; border-radius: 4px; width: 70%; }}
    .sidebar-step {{ padding: 10px; border-radius: 8px; margin-bottom: 5px; }}
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "selection"

# --- 1. LOGIN (Disposition) ---
if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center;'>⚖️ LegalOS Access</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        e = st.text_input("Email")
        p = st.text_input("Mot de passe", type="password")
        if st.form_submit_button("Entrer"):
            res = login_user(e, p)
            if res:
                st.session_state.auth, st.session_state.user_name, st.session_state.is_premium, st.session_state.user_email = True, res[0], res[1], e
                st.rerun()
    st.stop()

# --- 2. CABINET (Disposition) ---
if st.session_state.page == "selection":
    st.title(f"📂 Cabinet de {st.session_state.user_name}")
    if st.button("➕ Nouveau Dossier"):
        st.session_state.page = "cabinet"; st.rerun()
    
    st.subheader("Vos travaux récents")
    dossiers = get_user_dossiers(st.session_state.user_email)
    for d in dossiers:
        with st.expander(f"📁 {d[0]} - {d[1]}"):
            st.write(d[3])
            if st.button(f"Ouvrir {d[0]}", key=d[0]):
                st.session_state.page = "cabinet"; st.rerun()
    st.stop()

# --- 3. CABINET FREEMAN (Disposition 2 colonnes) ---
with st.sidebar:
    st.title("⚖️ MÉTHODE FREEMAN")
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", "5. Risques", "6. Amiable", "7. Stratégie", "8. Rédaction", "9. Audience", "10. Jugement", "11. Recours"]
    choice = st.radio("Navigation du dossier :", steps)
    idx = int(choice.split('.')[0])
    if not st.session_state.is_premium:
        st.link_button("🚀 PASSER PREMIUM", STRIPE_LINK)

# Verrouillage Freemium (Après étape 3)
if idx > 3 and not st.session_state.is_premium:
    st.warning("🔒 Cette étape est réservée aux membres Premium.")
    st.link_button("Débloquer la méthode complète", STRIPE_LINK)
    st.stop()

# CONTENU (Disposition identique)
st.title(f"{choice}")
col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.subheader("📄 Détails du Dossier")
    with st.form("analysis_form"):
        nom_d = st.text_input("Nom du dossier", value="Nouveau Dossier")
        faits = st.text_area("Décrivez les faits précisément :", height=300)
        if st.form_submit_button("🚀 ANALYSE EXPERTE KAREEM"):
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Tu es Kareem. Donne la branche du droit et un conseil stratégique court."},
                          {"role": "user", "content": faits}]
            )
            st.session_state.analysis = chat.choices[0].message.content
            save_dossier(st.session_state.user_email, nom_d, faits, "Droit Civil")
            st.rerun()

with col_right:
    st.subheader("🎯 Intelligence Kareem")
    c1, c2 = st.columns(2)
    with c1: st.metric("Branche détectée", "DROIT CIVIL")
    with c2: st.metric("Chances de succès", "85%")
    
    st.markdown('<div class="status-bar"><div class="status-fill"></div></div>', unsafe_allow_html=True)
    
    if 'analysis' in st.session_state:
        st.markdown(f"""
        <div class="kareem-card">
            <p style="color:#10b981; font-weight:bold;">🤖 Kareem IA :</p>
            {st.session_state.analysis}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("En attente de l'analyse à gauche...")
