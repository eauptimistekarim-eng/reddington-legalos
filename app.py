import streamlit as st
import time
from groq import Groq
from database import *

# --- CONFIGURATION ---
init_db()
GROQ_KEY = "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"
STRIPE_LINK = "https://buy.stripe.com/9B6aEW6QF6Z6bFz3RY6c001"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS - Kareem", layout="wide")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .kareem-card { background-color: #1e293b; padding: 25px; border-radius: 15px; border: 1px solid #334155; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; }
    .slogan { color: #94a3b8; font-style: italic; font-size: 1.1em; text-align: center; margin-bottom: 40px; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; justify-content: center; }
    </style>
    """, unsafe_allow_html=True)

def typewriter(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold; margin-bottom:10px;">🤖 Kareem IA :</p>{full_text}▌</div>', unsafe_allow_html=True)
        time.sleep(0.01)
    container.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold; margin-bottom:10px;">🤖 Kareem IA :</p>{text}</div>', unsafe_allow_html=True)

# --- AUTHENTIFICATION ---
if 'auth' not in st.session_state:
    st.markdown("<h1 style='text-align:center; font-size: 3em;'>⚖️ LegalOS</h1>", unsafe_allow_html=True)
    st.markdown("<p class='slogan'>L'intelligence juridique au service de la méthode Reddington.</p>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["Connexion", "Inscription", "Clé à usage unique"])
    
    with t1:
        with st.form("login_form"):
            e, p = st.text_input("Email"), st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Entrer dans le cabinet"):
                res = login_user(e, p)
                if res:
                    st.session_state.auth, st.session_state.user_name, st.session_state.is_premium, st.session_state.user_email = True, res[0], res[1], e
                    st.rerun()
                else: st.error("Identifiants incorrects.")
    
    with t2:
        with st.form("reg_form"):
            n, e, p = st.text_input("Nom"), st.text_input("Email"), st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Créer mon compte"):
                if register_user(e, p, n): st.success("Compte créé ! Connectez-vous.")
                else: st.error("Cet email est déjà utilisé.")
    
    with t3:
        st.text_input("Entrez votre clé d'accès")
        st.button("Activer la clé")
    st.stop()

# --- CABINET ---
if 'page' not in st.session_state: st.session_state.page = "selection"

if st.session_state.page == "selection":
    st.title(f"📂 Cabinet de {st.session_state.user_name}")
    if st.button("➕ Nouveau Dossier"):
        st.session_state.current_dossier = f"Affaire_{int(time.time())}"
        st.session_state.page = "cabinet"; st.rerun()
    
    st.divider()
    dossiers = get_user_dossiers(st.session_state.user_email)
    for d in dossiers:
        if st.button(f"📁 {d[0]}", key=d[0]):
            st.session_state.current_dossier = d[0]
            st.session_state.page = "cabinet"; st.rerun()
    st.stop()

# --- MÉTHODE REDDINGTON (11 ÉTAPES) ---
with st.sidebar:
    st.title("MÉTHODE REDDINGTON")
    if st.button("⬅️ Menu Principal"): st.session_state.page = "selection"; st.rerun()
    
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", "5. Risques", 
             "6. Amiable", "7. Stratégie", "8. Rédaction", "9. Audience", "10. Jugement", "11. Recours"]
    choice = st.radio("Progression :", steps)
    idx = int(choice.split('.')[0])
    
    if not st.session_state.is_premium and idx > 3:
        st.warning("🔒 Section réservée aux membres Premium.")
        st.link_button("🚀 DEVENIR PREMIUM", STRIPE_LINK)
        st.stop()

# --- INTERFACE DE TRAVAIL ---
st.header(f"Dossier : {st.session_state.current_dossier} — {choice}")

# Charger les données spécifiques à cette étape
faits_etape, analyse_etape = get_step_specific_data(st.session_state.user_email, st.session_state.current_dossier, idx)

col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.subheader("📝 Saisie des informations")
    with st.form(f"form_step_{idx}"):
        # Champ de texte indépendant par étape
        faits_input = st.text_area("Éléments factuels pour cette étape :", value=faits_etape, height=400)
        
        if st.form_submit_button("🛠️ ANALYSE PAR KAREEM"):
            # Récupérer tout le contexte pour l'IA
            contexte_complet = get_full_dossier_context(st.session_state.user_email, st.session_state.current_dossier)
            
            prompt = f"VOICI LE DOSSIER COMPLET À CE JOUR :\n{contexte_complet}\n\nMISSION ACTUELLE : Étape {choice}\nNOUVELLES DONNÉES : {faits_input}\nConsigne : Agis comme mon avocat, analyse et conseille-moi sur cette étape précise."
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Tu es Kareem, une IA avocat experte. Ton ton est professionnel, précis et stratégique."},
                          {"role": "user", "content": prompt}]
            )
            
            res_text = response.choices[0].message.content
            save_step_progress(st.session_state.user_email, st.session_state.current_dossier, faits_input, res_text, idx)
            st.session_state.last_ia = res_text
            st.session_state.trigger_type = True
            st.rerun()

with col_right:
    st.subheader("🎯 Intelligence Kareem")
    
    # On affiche soit la nouvelle analyse (typewriter), soit l'ancienne (statique)
    ia_content = st.session_state.get('last_ia', analyse_etape)
    
    if ia_content:
        if st.session_state.get('trigger_type', False):
            typewriter(ia_content)
            st.session_state.trigger_type = False
        else:
            st.markdown(f'<div class="kareem-card"><p style="color:#10b981; font-weight:bold; margin-bottom:10px;">🤖 Kareem IA :</p>{ia_content}</div>', unsafe_allow_html=True)
    else:
        st.info("Kareem attend vos informations pour analyser cette étape.")
