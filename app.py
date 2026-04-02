import streamlit as st
import pandas as pd
import time
import PyPDF2
from database import init_db, login_user, add_user, upgrade_to_premium

# --- INITIALISATION ---
init_db()
st.set_page_config(page_title="LegalOS - Kareem IA", layout="wide")

# --- FONCTION TYPEWRITER (L'ÂME DE KAREEM) ---
def typewriter(text, speed=0.01):
    container = st.empty()
    displayed_text = ""
    for char in text:
        displayed_text += char
        container.markdown(f"""
            <div class="kareem-box">
                <p style="margin-bottom:0;">🤖 <b>Kareem :</b></p>
                {displayed_text}▌
            </div>
            """, unsafe_allow_html=True)
        time.sleep(speed)
    container.markdown(f'<div class="kareem-box"><p style="margin-bottom:0;">🤖 <b>Kareem :</b></p>{displayed_text}</div>', unsafe_allow_html=True)

# --- LOGIQUE D'ANALYSE ---
def classifier_procedure(faits):
    if not faits: return "NON DÉFINI"
    t = faits.lower()
    if any(w in t for w in ["salaire", "travail", "licenciement", "patron", "prud'hommes"]): return "DROIT DU TRAVAIL"
    if any(w in t for w in ["loyer", "bail", "expulsion", "propriétaire"]): return "DROIT IMMOBILIER"
    return "DROIT CIVIL GÉNÉRAL"

# --- DESIGN "LEGALOS GOLD" ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    .kareem-box { 
        background-color: #161e2e; padding: 20px; border-radius: 12px; 
        border-left: 4px solid #10b981; font-family: 'Courier New', Courier, monospace;
        color: #10b981; line-height: 1.6; border: 1px solid #1e293b;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .stMetric { background: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    </style>
    """, unsafe_allow_html=True)

# --- MÉMOIRE DU DOSSIER (LIEN ENTRE ÉTAPES) ---
if 'dossier' not in st.session_state:
    st.session_state.dossier = {
        "faits": "", "branche": None, "score": 0, "objectif": None, "pieces": 0
    }

# --- AUTHENTIFICATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown('<p style="color:#10b981; font-size:2.5rem; font-weight:bold; text-align:center;">⚖️ LegalOS Access</p>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        e = st.text_input("Email", key="l_e")
        p = st.text_input("Mot de passe", type="password", key="l_p")
        if st.button("Se connecter"):
            res = login_user(e, p)
            if res:
                st.session_state.logged_in, st.session_state.user_name, st.session_state.is_premium = True, res[0], res[2]
                st.rerun()
    with t2: st.info("Espace de création de compte.")
    st.stop()

# --- SIDEBAR & NAVIGATION ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user_name}")
    st.divider()
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", "5. Risques", "6. Amiable", "7. Stratégie", "8. Rédaction", "9. Audience", "10. Jugement", "11. Recours"]
    selected_step = st.radio("MÉTHODE FREEMAN", steps)
    current_idx = int(selected_step.split('.')[0])
    st.divider()
    if st.button("Se déconnecter"):
        st.session_state.logged_in = False
        st.rerun()

# --- INTERFACE DE TRAVAIL ---
st.markdown(f'<p style="color:#10b981; font-size:1.8rem; font-weight:bold;">{selected_step}</p>', unsafe_allow_html=True)
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    if current_idx == 1:
        st.subheader("📄 Qualification du Dossier")
        st.radio("État :", ["Nouveau dossier", "En cours", "À finaliser"], horizontal=True)
        file = st.file_uploader("Ajouter une preuve (PDF)", type="pdf")
        txt = st.text_area("Récit des faits :", height=250, value=st.session_state.dossier["faits"])
        
        if st.button("🚀 LANCER L'ANALYSE KAREEM"):
            st.session_state.dossier["faits"] = txt
            st.session_state.dossier["branche"] = classifier_procedure(txt)
            st.session_state.dossier["score"] = 45 if not file else 85
            st.session_state.trigger_msg = f"Analyse terminée. Ce dossier relève du **{st.session_state.dossier['branche']}**. \n\nMon diagnostic montre un potentiel de succès de {st.session_state.dossier['score']}%. Pour avancer, nous devons maintenant définir votre **Objectif** à l'étape 2."
            st.rerun()

    elif current_idx == 2:
        st.subheader("🎯 Définition de l'Objectif")
        if not st.session_state.dossier["branche"]:
            st.warning("⚠️ Veuillez qualifier le dossier à l'étape 1 d'abord.")
        else:
            objs = ["Rappel de salaires", "Indemnités de licenciement", "Réintégration"] if st.session_state.dossier["branche"] == "DROIT DU TRAVAIL" else ["Dommages et intérêts", "Exécution forcée"]
            choix = st.selectbox("Choisissez votre objectif principal :", objs)
            if st.button("🎯 Fixer l'Objectif"):
                st.session_state.dossier["objectif"] = choix
                st.session_state.trigger_msg = f"Objectif enregistré : **{choix}**. \n\nC'est un choix cohérent avec un dossier de {st.session_state.dossier['branche']}. Je vais maintenant préparer la **Base Légale** (Étape 3) pour soutenir cette demande."
                st.rerun()

with col_right:
    st.subheader("🤖 Analyse de l'IA")
    
    # Affichage des métriques si l'analyse est faite
    if st.session_state.dossier["branche"]:
        c1, c2 = st.columns(2)
        c1.metric("Branche", st.session_state.dossier["branche"])
        c2.metric("Chances", f"{st.session_state.dossier['score']}%")
        st.progress(st.session_state.dossier["score"] / 100)

    # Zone de dialogue Kareem
    if "trigger_msg" in st.session_state:
        typewriter(st.session_state.trigger_msg)
        del st.session_state.trigger_msg
    elif st.session_state.dossier["branche"]:
        st.markdown(f'<div class="kareem-box">🤖 <b>Kareem :</b><br>Dossier prêt pour l\'étape {current_idx}. J\'attends vos instructions à gauche.</div>', unsafe_allow_html=True)
    else:
        st.info("Kareem attend l'analyse des faits pour commencer le guidage...")
