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

# --- DESIGN FIGÉ (IDENTIQUE À TES CAPTURES) ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .kareem-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; }
    .status-bar { background-color: #334155; height: 10px; border-radius: 5px; margin: 15px 0; overflow: hidden; }
    .status-fill { background: linear-gradient(90deg, #10b981, #3b82f6); height: 100%; border-radius: 5px; width: 85%; }
    .stButton>button { background-color: #10b981 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DES VARIABLES DE SESSION ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'page' not in st.session_state:
    st.session_state.page = "selection"

# --- 1. FORMULAIRE DE CONNEXION (AFFICHAGE FORCÉ SI NON CONNECTÉ) ---
if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center; color:#10b981;'>⚖️ Connexion LegalOS</h2>", unsafe_allow_html=True)
    
    # Centre le formulaire
    _, col_center, _ = st.columns([1, 2, 1])
    with col_center:
        with st.form("login_form"):
            email = st.text_input("Votre Email")
            password = st.text_input("Votre Mot de passe", type="password")
            submit = st.form_submit_button("Entrer dans le Cabinet (Entrée)")
            
            if submit:
                res = login_user(email, password)
                if res:
                    st.session_state.auth = True
                    st.session_state.user_name = res[0]
                    st.session_state.is_premium = res[1]
                    st.session_state.user_email = email
                    st.rerun() # Relance pour afficher le cabinet
                else:
                    st.error("Email ou mot de passe incorrect.")
    st.stop() # Arrête le script ici tant que l'utilisateur n'est pas loggé

# --- 2. CABINET (SÉLECTION DES DOSSIERS) ---
if st.session_state.page == "selection":
    st.title(f"📂 Cabinet de {st.session_state.user_name}")
    if st.button("➕ Créer un nouveau dossier"):
        st.session_state.page = "cabinet"
        st.rerun()
    
    st.divider()
    dossiers = get_user_dossiers(st.session_state.user_email)
    if dossiers:
        for d in dossiers:
            with st.expander(f"📁 {d[0]} - {d[1]}"):
                if st.button(f"Ouvrir {d[0]}", key=d[0]):
                    st.session_state.current_dossier = d[0]
                    st.session_state.page = "cabinet"
                    st.rerun()
    else:
        st.info("Aucun dossier trouvé. Commencez par en créer un.")
    st.stop()

# --- 3. MODE AVOCAT (MÉTHODE FREEMAN PROGRESSIVE) ---
with st.sidebar:
    st.title("MÉTHODE FREEMAN")
    if st.button("⬅️ Retour au Cabinet"):
        st.session_state.page = "selection"
        st.rerun()
    
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", "5. Risques", "6. Stratégie", "7. Rédaction"]
    choice = st.radio("Progression :", steps)
    idx = int(choice.split('.')[0])
    
    if not st.session_state.is_premium and idx > 3:
        st.warning("🔒 Étape Premium")
        st.link_button("🚀 Débloquer", STRIPE_LINK)
        st.stop()

# --- INTERFACE DE TRAVAIL (2 COLONNES) ---
st.header(f"Dossier : {st.session_state.get('current_dossier', 'Sans titre')} - {choice}")
col_l, col_r = st.columns(2, gap="large")

with col_l:
    st.subheader("📝 Action de l'Avocat")
    with st.form("action_form"):
        faits = st.text_area("Précisions pour cette étape :", height=300)
        
        if st.form_submit_button("🔨 Faire progresser l'analyse"):
            _, historique = get_full_history(st.session_state.user_email, st.session_state.current_dossier)
            
            # Kareem adapte son conseil selon l'étape et l'historique
            prompt = f"Historique : {historique}\nÉtape : {choice}\nNouveaux faits : {faits}"
            
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Tu es Kareem, avocat expert en méthode Freeman. Sois précis et stratégique."},
                          {"role": "user", "content": prompt}]
            )
            
            st.session_state.last_res = resp.choices[0].message.content
            save_step_progress(st.session_state.user_email, st.session_state.current_dossier, faits, st.session_state.last_res, idx)
            st.rerun()

with col_r:
    st.subheader("🎯 Intelligence Kareem")
    st.metric("Fiabilité Stratégique", f"{65 + idx*5}%")
    st.markdown('<div class="status-bar"><div class="status-fill"></div></div>', unsafe_allow_html=True)
    
    if 'last_res' in st.session_state:
        # Effet machine à écrire simplifié pour la stabilité
        st.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold;">🤖 Kareem :</p>{st.session_state.last_res}</div>', unsafe_allow_html=True)
