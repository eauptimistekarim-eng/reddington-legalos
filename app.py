import streamlit as st
from groq import Groq
from database import init_db, login_user, save_dossier, get_user_dossiers

# --- CONFIGURATION ---
init_db()
GROQ_KEY = "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" # Ta clé
STRIPE_LINK = "https://buy.stripe.com/9B6aEW6QF6Z6bFz3RY6c001"

client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS - Kareem IA", layout="wide")

# --- DESIGN STRICT (Inspiré de image_35bcfe.jpg) ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .kareem-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; }
    .status-bar { background-color: #334155; height: 10px; border-radius: 5px; margin: 15px 0; }
    .status-fill { background: linear-gradient(90deg, #10b981, #3b82f6); height: 100%; border-radius: 5px; width: 85%; }
    .sidebar-step { padding: 8px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "selection"

# --- LOGIN ---
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

# --- CABINET (Dispo image_365250.png corrigée) ---
if st.session_state.page == "selection":
    st.title(f"📂 Cabinet de {st.session_state.user_name}")
    if st.button("➕ Nouveau Dossier"):
        st.session_state.page = "cabinet"; st.rerun()
    
    st.divider()
    dossiers = get_user_dossiers(st.session_state.user_email)
    for d in dossiers:
        with st.expander(f"📁 {d[0]} - {d[1]} ({d[2]})"):
            st.write(d[3])
            if st.button(f"Ouvrir {d[0]}", key=d[0]):
                st.session_state.page = "cabinet"; st.rerun()
    st.stop()

# --- CABINET FREEMAN (2 colonnes strictes) ---
with st.sidebar:
    st.title("⚖️ LegalOS")
    if st.button("⬅️ Liste des dossiers"): st.session_state.page = "selection"; st.rerun()
    st.divider()
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", "5. Risques", "6. Amiable", "7. Stratégie", "8. Rédaction", "9. Audience", "10. Jugement", "11. Recours"]
    choice = st.radio("Navigation :", steps)
    idx = int(choice.split('.')[0])
    if not st.session_state.is_premium:
        st.link_button("🚀 DEVENIR PREMIUM", STRIPE_LINK)

# Verrouillage Freemium après l'étape 3
if idx > 3 and not st.session_state.is_premium:
    st.markdown(f'<div style="background:#450a0a; padding:20px; border-radius:10px; border:1px solid #ef4444; text-align:center;">'
                f'<h3>🔒 Étape Premium</h3><p>Débloquez la suite avec votre abonnement.</p>'
                f'<a href="{STRIPE_LINK}" target="_blank" style="color:white; font-weight:bold;">S\'ABONNER ICI</a></div>', unsafe_allow_html=True)
    st.stop()

st.title(choice)
col_l, col_r = st.columns(2, gap="large")

with col_l:
    st.subheader("📄 Saisie des faits")
    with st.form("kareem_analysis"):
        nom_d = st.text_input("Nom du dossier", value="Affaire en cours")
        faits = st.text_area("Décrivez la situation :", height=300)
        if st.form_submit_button("🚀 ANALYSE EXPERTE KAREEM"):
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Tu es Kareem. Donne la branche du droit et un conseil court."},
                          {"role": "user", "content": faits}]
            )
            st.session_state.analysis = chat.choices[0].message.content
            save_dossier(st.session_state.user_email, nom_d, faits, "Droit Civil")
            st.rerun()

with col_r:
    st.subheader("🎯 Intelligence Kareem")
    st.metric("Chances de succès", "85%") # Exemple statique comme image_35bcfe.jpg
    st.markdown('<div class="status-bar"><div class="status-fill"></div></div>', unsafe_allow_html=True)
    
    if 'analysis' in st.session_state:
        st.markdown(f'<div class="kareem-card"><p style="color:#10b981;">🤖 Kareem :</p>{st.session_state.analysis}</div>', unsafe_allow_html=True)
    else:
        st.info("Kareem attend vos instructions à gauche.")
