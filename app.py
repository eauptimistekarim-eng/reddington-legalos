import streamlit as st
import time
from database import init_db, login_user, add_user, save_dossier, get_user_dossiers

init_db()
st.set_page_config(page_title="LegalOS - Kareem IA", layout="wide")

# --- STYLE & LOGO ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .kareem-box { 
        background-color: #161e2e; padding: 20px; border-radius: 12px; 
        border-left: 4px solid #10b981; font-family: 'Courier New', monospace;
        color: #10b981; border: 1px solid #1e293b;
    }
    .logo-text { font-size: 3rem; font-weight: bold; color: #10b981; text-align: center; margin-bottom: 0px; }
    .sub-logo { text-align: center; color: #64748b; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTEUR JURIDIQUE ---
def analyse_universelle(faits):
    f = faits.lower()
    if any(w in f for w in ["vol", "agression", "plainte", "police"]): return "DROIT PÉNAL", "Code Pénal", "Art. 121-1"
    if any(w in f for w in ["salaire", "licenciement", "patron", "travail"]): return "DROIT DU TRAVAIL", "Code du Travail", "Art. L1232-1"
    if any(w in f for w in ["loyer", "bail", "propriétaire", "appartement"]): return "DROIT IMMOBILIER", "Loi du 6 juillet 1989", "Art. 7"
    return "DROIT CIVIL", "Code Civil", "Art. 1240"

def typewriter(text):
    container = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        container.markdown(f'<div class="kareem-box">🤖 <b>Kareem :</b><br>{displayed}▌</div>', unsafe_allow_html=True)
        time.sleep(0.01)
    container.markdown(f'<div class="kareem-box">🤖 <b>Kareem :</b><br>{displayed}</div>', unsafe_allow_html=True)

# --- GESTION SESSION (Pas de reconnexion au refresh) ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "selection"

# 1. AUTHENTIFICATION
if not st.session_state.auth:
    st.markdown('<p class="logo-text">⚖️ LegalOS</p><p class="sub-logo">Intelligence Artificielle Juridique</p>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        with st.form("login"):
            e = st.text_input("Email")
            p = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Entrer"): # Touche Entrée fonctionne ici
                res = login_user(e, p)
                if res:
                    st.session_state.auth, st.session_state.user_name, st.session_state.user_email = True, res[0], e
                    st.rerun()
                else: st.error("Identifiants incorrects.")
    with t2:
        with st.form("signup"):
            nn, ne, np = st.text_input("Nom"), st.text_input("Email"), st.text_input("Pass", type="password")
            if st.form_submit_button("S'inscrire"):
                if add_user(ne, np, nn): st.success("Compte créé !")
    st.stop()

# 2. SÉLECTION / RETROUVER SES TRAVAUX
if st.session_state.page == "selection":
    st.markdown(f"## 📂 Cabinet de {st.session_state.user_name}")
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        if st.button("➕ Nouveau dossier", use_container_width=True):
            st.session_state.page = "cabinet"; st.rerun()
    
    st.divider()
    st.subheader("Vos travaux récents")
    dossiers = get_user_dossiers(st.session_state.user_email)
    if dossiers:
        for d in dossiers:
            with st.expander(f"📁 {d[0]} - {d[1]} ({d[2]})"):
                st.write(f"**Faits :** {d[3]}")
                if st.button(f"Ouvrir {d[0]}", key=d[0]):
                    st.session_state.page = "cabinet"
                    st.session_state.current_dossier = d
                    st.rerun()
    else: st.info("Aucun dossier enregistré.")
    st.stop()

# 3. CABINET (11 ÉTAPES)
with st.sidebar:
    st.markdown("### ⚖️ LegalOS")
    if st.button("⬅️ Retour au Cabinet"):
        st.session_state.page = "selection"; st.rerun()
    st.divider()
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", "5. Risques", "6. Amiable", "7. Stratégie", "8. Rédaction", "9. Audience", "10. Jugement", "11. Recours"]
    choice = st.radio("MÉTHODE FREEMAN", steps)
    idx = int(choice.split('.')[0])

st.markdown(f'<p style="color:#10b981; font-size:1.8rem; font-weight:bold;">{choice}</p>', unsafe_allow_html=True)
col_l, col_r = st.columns([1, 1], gap="large")

with col_l:
    if idx == 1:
        with st.form("analyse_form"): # Support touche Entrée
            nom_d = st.text_input("Nom du dossier (ex: Litige Martin)")
            faits = st.text_area("Exposez les faits :", height=250)
            sub = st.form_submit_button("🚀 LANCER L'ANALYSE")
            if sub:
                br, code, art = analyse_universelle(faits)
                save_dossier(st.session_state.user_email, nom_d, faits, br)
                st.session_state.res = {"br": br, "art": art, "msg": f"Analyse Freeman terminée. Domaine : {br}. Référence : {art}."}
                st.rerun()

with col_r:
    st.subheader("🤖 Kareem IA")
    if 'res' in st.session_state:
        st.metric("Branche", st.session_state.res['br'])
        typewriter(st.session_state.res['msg'])
