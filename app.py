import streamlit as st
import sqlite3
import bcrypt
import time
from groq import Groq

# --- CONFIGURATION ---
GROQ_KEY = "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"
client = Groq(api_key=GROQ_KEY)

# --- BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('legalos_final.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT, name TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS dossiers (nom TEXT, user_email TEXT, PRIMARY KEY(nom, user_email))')
    c.execute('CREATE TABLE IF NOT EXISTS steps (user_email TEXT, dossier_nom TEXT, step_idx INTEGER, faits TEXT, analyse TEXT, PRIMARY KEY(user_email, dossier_nom, step_idx))')
    conn.commit()
    conn.close()

def login(e, p):
    conn = sqlite3.connect('legalos_final.db')
    c = conn.cursor()
    c.execute("SELECT name, password FROM users WHERE email=?", (e,))
    res = c.fetchone()
    conn.close()
    if res and bcrypt.checkpw(p.encode('utf-8'), res[1]): return res[0]
    return None

def register(e, p, n):
    conn = sqlite3.connect('legalos_final.db')
    c = conn.cursor()
    hashed = bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (e, hashed, n))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

# --- INTERFACE & STYLE ---
st.set_page_config(page_title="LegalOS - Méthode Freeman", layout="wide")
init_db()

st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #e2e8f0; }
    .kareem-card { background: #161b22; border-left: 5px solid #10b981; padding: 20px; border-radius: 10px; font-family: 'Courier New', Courier, monospace; }
    .stButton>button { border-radius: 5px; height: 3em; background: #10b981; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

def typewriter(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(f'<div class="kareem-card"><b style="color:#10b981;">🤖 Kareem IA :</b><br>{full_text}▌</div>', unsafe_allow_html=True)
        time.sleep(0.005)
    container.markdown(f'<div class="kareem-card"><b style="color:#10b981;">🤖 Kareem IA :</b><br>{text}</div>', unsafe_allow_html=True)

# --- CONNEXION ---
if not st.session_state.auth:
    st.title("⚖️ LegalOS")
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        e = st.text_input("Email")
        p = st.text_input("Mot de passe", type="password")
        if st.button("Accéder au Cabinet"):
            name = login(e, p)
            if name:
                st.session_state.auth, st.session_state.user_name, st.session_state.user_email = True, name, e
                st.rerun()
    with t2:
        n_r, e_r, p_r = st.text_input("Nom"), st.text_input("Email "), st.text_input("Pass", type="password")
        if st.button("Créer compte"):
            if register(e_r, p_r, n_r): st.success("OK ! Connectez-vous.")
    st.stop()

# --- NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "cabinet"

if st.session_state.page == "cabinet":
    st.title(f"📂 Dossiers de {st.session_state.user_name}")
    if st.button("➕ NOUVELLE AFFAIRE (FREEMAN)"):
        st.session_state.current_dossier = f"Affaire_{int(time.time())}"
        st.session_state.page = "travail"; st.rerun()
    
    conn = sqlite3.connect('legalos_final.db')
    c = conn.cursor()
    c.execute("SELECT nom FROM dossiers WHERE user_email=?", (st.session_state.user_email,))
    for i, d in enumerate(c.fetchall()):
        if st.button(f"📁 {d[0]}", key=f"d_{i}"):
            st.session_state.current_dossier = d[0]
            st.session_state.page = "travail"; st.rerun()
    conn.close()
    st.stop()

# --- WORKSPACE ---
with st.sidebar:
    st.header("MÉTHODE FREEMAN")
    if st.button("⬅️ Cabinet"): st.session_state.page = "cabinet"; st.rerun()
    steps = ["1. Qualification", "2. Objectif", "3. Base Légale", "4. Inventaire", "5. Risques", "6. Amiable", "7. Stratégie", "8. Rédaction", "9. Audience", "10. Jugement", "11. Recours"]
    choice = st.radio("Progression :", steps)
    idx = steps.index(choice) + 1

st.header(f"💼 Dossier : {st.session_state.current_dossier}")

# Charger data
conn = sqlite3.connect('legalos_final.db')
c = conn.cursor()
c.execute("SELECT faits, analyse FROM steps WHERE user_email=? AND dossier_nom=? AND step_idx=?", (st.session_state.user_email, st.session_state.current_dossier, idx))
res = c.fetchone()
conn.close()
f_db, a_db = res if res else ("", "")

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"📍 Étape {choice}")
    input_text = st.text_area("Matière brute pour cette étape :", value=f_db, height=400)
    
    if st.button("⚡ ACTION KAREEM"):
        # RECUPERER TOUT LE CONTEXTE PASSÉ
        conn = sqlite3.connect('legalos_final.db')
        c = conn.cursor()
        c.execute("SELECT step_idx, faits, analyse FROM steps WHERE user_email=? AND dossier_nom=? AND step_idx < ?", (st.session_state.user_email, st.session_state.current_dossier, idx))
        history = "\n".join([f"E{r[0]}: {r[1]} -> {r[2]}" for r in c.fetchall()])
        conn.close()

        # MISSIONS STRICTES PAR ETAPE
        missions = {
            1: "Analyse les faits et donne EXCLUSIVEMENT la qualification juridique (ex: Licenciement sans cause réelle). Ne parle pas de stratégie ici.",
            2: "Définis l'OBJECTIF principal : que voulons-nous gagner précisément ?",
            3: "Identifie les ARTICLES DE LOI applicables. Cite les codes.",
            4: "Fais l'inventaire des preuves. Dis ce qu'il manque.",
            5: "Liste les RISQUES : pourquoi pourrions-nous perdre ?",
            6: "Rédige une proposition de SOLUTION AMIABLE (transaction).",
            7: "AVOCAT DU DIABLE : Attaque le dossier. Trouve les failles que l'adversaire va exploiter.",
            8: "Génère un MODÈLE DE RÉDACTION juridique complet.",
            9: "AUDIENCE : Simule le juge. Pose 3 questions pièges basées sur les faits.",
            10: "Analyse le JUGEMENT rendu (si l'utilisateur le saisit).",
            11: "RECOURS : Propose une stratégie d'appel ou de contestation."
        }

        prompt = f"""Tu es Kareem, Directeur Juridique de haut niveau. 
        MÉTHODE : Freeman.
        HISTORIQUE : {history}
        ÉTAPE ACTUELLE : {choice}
        MISSION : {missions[idx]}
        INPUT : {input_text}
        
        CONSIGNE : Ne réponds QUE sur l'objectif de l'étape actuelle. Sois tranchant, directif et expert."""

        resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        full_ana = resp.choices[0].message.content
        
        # Sauvegarde
        conn = sqlite3.connect('legalos_final.db')
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO dossiers VALUES (?,?)", (st.session_state.current_dossier, st.session_state.user_email))
        c.execute("INSERT OR REPLACE INTO steps VALUES (?,?,?,?,?)", (st.session_state.user_email, st.session_state.current_dossier, idx, input_text, full_ana))
        conn.commit()
        conn.close()
        
        st.session_state.last_ia = full_ana
        st.session_state.trigger_type = True
        st.rerun()

with col2:
    st.subheader("🤖 Analyse de Kareem")
    display_text = st.session_state.get('last_ia', a_db)
    if display_text:
        if st.session_state.get('trigger_type', False):
            typewriter(display_text)
            st.session_state.trigger_type = False
        else:
            st.markdown(f'<div class="kareem-card"><b style="color:#10b981;">🤖 Kareem IA :</b><br>{display_text}</div>', unsafe_allow_html=True)
