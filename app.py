import streamlit as st
import time
import re
import PyPDF2
from database import init_db, login_user, add_user, upgrade_to_premium, send_welcome_email

# --- INITIALISATION ---
init_db()
st.set_page_config(page_title="LegalOS - Kareem IA", layout="wide")

# --- CERVEAU DE KAREEM (ANALYSE PERSONNALISÉE) ---
def analyse_freeman(faits):
    # Extraction de données précises
    dates = re.findall(r'\d{2}/\d{2}/\d{4}', faits)
    montants = re.findall(r'\d+[\s]*€', faits)
    
    # Détection de branche et conseil spécifique
    f_low = faits.lower()
    if any(w in f_low for w in ["salaire", "licenciement", "prud'hommes", "travail"]):
        branche = "DROIT DU TRAVAIL"
        conseil = "Attention : En matière de contestation de licenciement, le délai est souvent de 12 mois."
    elif any(w in f_low for w in ["loyer", "bail", "expulsion", "appartement"]):
        branche = "DROIT IMMOBILIER"
        conseil = "Il est impératif de vérifier si une mise en demeure a été signifiée par acte d'huissier ou LRAR."
    else:
        branche = "DROIT CIVIL GÉNÉRAL"
        conseil = "Nous devrons prouver le préjudice et le lien de causalité selon l'article 1240 du Code Civil."

    msg = f"Analyse terminée pour votre dossier de {branche}. \n\n"
    if dates: msg += f"📅 Dates clés détectées : {', '.join(dates)}. \n"
    if montants: msg += f"💰 Enjeu financier repéré : {montants[0]}. \n\n"
    msg += f"💡 **Conseil stratégique de Kareem :** {conseil} \n\nPassons à l'étape 2."
    
    return branche, msg

# --- EFFET MACHINE À ÉCRIRE ---
def typewriter(text):
    container = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        container.markdown(f'<div class="kareem-box">🤖 <b>Kareem :</b><br>{displayed}▌</div>', unsafe_allow_html=True)
        time.sleep(0.01)
    container.markdown(f'<div class="kareem-box">🤖 <b>Kareem :</b><br>{displayed}</div>', unsafe_allow_html=True)

# --- DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    .kareem-box { 
        background-color: #161e2e; padding: 20px; border-radius: 12px; 
        border-left: 4px solid #10b981; font-family: 'Courier New', monospace;
        color: #10b981; border: 1px solid #1e293b; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .stMetric { background: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION & AUTH ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'dossier' not in st.session_state: st.session_state.dossier = {"faits": "", "branche": None, "msg": "", "score": 0}

if not st.session_state.logged_in:
    st.markdown('<p style="color:#10b981; font-size:2.5rem; font-weight:bold; text-align:center;">⚖️ LegalOS Access</p>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        el = st.text_input("Email", key="l_e")
        pl = st.text_input("Mot de passe", type="password", key="l_p")
        if st.button("Se connecter"):
            res = login_user(el, pl)
            if res:
                st.session_state.logged_in, st.session_state.user_name, st.session_state.is_premium = True, res[0], res[2]
                st.rerun()
    with t2:
        nn = st.text_input("Nom Complet")
        ne = st.text_input("Email")
        np = st.text_input("Mot de passe", type="password")
        if st.button("Créer mon compte"):
            if add_user(ne, np, nn):
                send_welcome_email(ne, nn) # Envoi du mail réel
                st.success("Compte créé ! Un mail de bienvenue vous a été envoyé.")
    st.stop()

# --- NAVIGATION ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user_name}")
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", "5. Risques", "6. Amiable", "7. Stratégie", "8. Rédaction", "9. Audience", "10. Jugement", "11. Recours"]
    choice = st.radio("MÉTHODE FREEMAN", steps)
    idx = int(choice.split('.')[0])
    if st.button("Déconnexion"):
        st.session_state.logged_in = False
        st.rerun()

# --- CABINET DE TRAVAIL ---
st.markdown(f'<p style="color:#10b981; font-size:1.8rem; font-weight:bold;">{choice}</p>', unsafe_allow_html=True)
col_l, col_r = st.columns([1, 1], gap="large")

with col_l:
    if idx == 1:
        st.subheader("📄 Qualification du Dossier")
        txt = st.text_area("Décrivez les faits (incluez dates et montants) :", height=300, value=st.session_state.dossier["faits"])
        if st.button("🚀 ANALYSE EXPERTE KAREEM"):
            st.session_state.dossier["faits"] = txt
            b, m = analyse_freeman(txt)
            st.session_state.dossier["branche"] = b
            st.session_state.dossier["msg"] = m
            st.session_state.dossier["score"] = 65 if len(txt) > 200 else 40
            st.rerun()

    elif idx == 2:
        st.subheader("🎯 Objectif Juridique")
        if not st.session_state.dossier["branche"]: st.warning("Passez d'abord par l'étape 1.")
        else:
            obj = st.selectbox("Sélectionnez l'objectif :", ["Rappel de salaire", "Indemnités", "Dommages & Intérêts"])
            if st.button("Valider"):
                st.session_state.dossier["msg"] = f"Objectif **{obj}** validé. Je prépare les articles de loi."
                st.rerun()

with col_r:
    st.subheader("🤖 Analyse de Kareem")
    if st.session_state.dossier["branche"]:
        c1, c2 = st.columns(2)
        c1.metric("Branche", st.session_state.dossier["branche"])
        c2.metric("Chances de succès", f"{st.session_state.dossier['score']}%")
        st.progress(st.session_state.dossier["score"] / 100)

    if st.session_state.dossier["msg"]:
        typewriter(st.session_state.dossier["msg"])
        st.session_state.dossier["msg"] = "" # Pour ne pas relancer l'animation à chaque clic
    elif st.session_state.dossier["branche"]:
        st.markdown(f'<div class="kareem-box">🤖 <b>Kareem :</b><br>J\'attends vos prochaines instructions pour l\'étape {idx}.</div>', unsafe_allow_html=True)
