import streamlit as st
import sqlite3
import bcrypt
import time
from groq import Groq

# ---------------- CONFIG ----------------
GROQ_KEY = "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"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS V2 - Freeman", layout="wide")

# ---------------- DB ----------------
def init_db():
    conn = sqlite3.connect('legalos_v2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT, name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS dossiers (nom TEXT, user_email TEXT, PRIMARY KEY(nom, user_email))''')
    c.execute('''CREATE TABLE IF NOT EXISTS steps (user_email TEXT, dossier_nom TEXT, step_idx INTEGER, faits TEXT, analyse TEXT, validated INTEGER DEFAULT 0, PRIMARY KEY(user_email, dossier_nom, step_idx))''')
    conn.commit()
    conn.close()

init_db()

# ---------------- AUTH ----------------
def login(e, p):
    conn = sqlite3.connect('legalos_v2.db')
    c = conn.cursor()
    c.execute("SELECT name, password FROM users WHERE email=?", (e,))
    res = c.fetchone()
    conn.close()
    if res and bcrypt.checkpw(p.encode(), res[1].encode() if isinstance(res[1], str) else res[1]):
        return res[0]
    return None

def register(e, p, n):
    conn = sqlite3.connect('legalos_v2.db')
    c = conn.cursor()
    hashed = bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (e, hashed, n))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
.stApp { background-color: #0b0f19; color: #e2e8f0; }
.kareem-card { background: #161b22; border-left: 5px solid #10b981; padding: 20px; border-radius: 10px; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

def typewriter(text):
    container = st.empty()
    out = ""
    for char in text:
        out += char
        container.markdown(f'<div class="kareem-card">🤖 KAREEM :<br><br>{out}▌</div>', unsafe_allow_html=True)
        time.sleep(0.001)
    container.markdown(f'<div class="kareem-card">🤖 KAREEM :<br><br>{text}</div>', unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "auth" not in st.session_state: st.session_state.auth = False
if "current_step_idx" not in st.session_state: st.session_state.current_step_idx = 1

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.title("⚖️ LegalOS V2")
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        e = st.text_input("Email")
        p = st.text_input("Pass", type="password")
        if st.button("Accéder"):
            name = login(e, p)
            if name:
                st.session_state.auth, st.session_state.user_email, st.session_state.user_name = True, e, name
                st.rerun()
    with t2:
        n_r, e_r, p_r = st.text_input("Nom"), st.text_input("Email "), st.text_input("Mdp", type="password")
        if st.button("Créer"):
            if register(e_r, p_r, n_r): st.success("Compte OK")
    st.stop()

# ---------------- NAV ----------------
if "page" not in st.session_state: st.session_state.page = "cabinet"

# ---------------- CABINET ----------------
if st.session_state.page == "cabinet":
    st.title(f"📂 Cabinet - {st.session_state.user_name}")
    if st.button("➕ Nouvelle affaire"):
        st.session_state.current_dossier = f"Affaire_{int(time.time())}"
        st.session_state.page, st.session_state.current_step_idx = "work", 1
        st.rerun()

    conn = sqlite3.connect('legalos_v2.db')
    c = conn.cursor()
    c.execute("SELECT nom FROM dossiers WHERE user_email=?", (st.session_state.user_email,))
    dossiers = [d[0] for d in c.fetchall()]
    conn.close()

    for d in dossiers:
        if st.button(f"📁 {d}"):
            st.session_state.current_dossier, st.session_state.page = d, "work"
            st.rerun()
    st.stop()

# ---------------- WORKSPACE ----------------
steps = ["Qualification", "Objectif", "Base légale", "Inventaire", "Risques", "Amiable", "Stratégie", "Rédaction", "Audience", "Jugement", "Recours"]

with st.sidebar:
    st.title("⚖️ Freeman")
    if st.button("⬅ Retour"):
        st.session_state.page = "cabinet"
        st.rerun()
    
    # Le radio est maintenant piloté par le session_state pour permettre le saut automatique
    step_choice = st.radio("Étapes", steps, index=st.session_state.current_step_idx - 1)
    st.session_state.current_step_idx = steps.index(step_choice) + 1
    idx = st.session_state.current_step_idx

st.title(f"💼 {st.session_state.current_dossier} - {step_choice}")

# Charger data
conn = sqlite3.connect('legalos_v2.db')
c = conn.cursor()
c.execute("SELECT faits, analyse, validated FROM steps WHERE user_email=? AND dossier_nom=? AND step_idx=?", (st.session_state.user_email, st.session_state.current_dossier, idx))
row = c.fetchone()
conn.close()
f_db, a_db, val_db = row if row else ("", "", 0)

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Saisie Étape {idx}")
    u_input = st.text_area("Informations :", value=f_db, height=300)
    if st.button("⚡ ANALYSE KAREEM"):
        missions = {1: "Qualification", 2: "Objectif financier", 3: "Articles de Loi", 7: "Avocat du Diable"}
        mission = missions.get(idx, "Analyse stratégique")
        
        prompt = f"Tu es Kareem. Mission Étape {idx} ({step_choice}) : {mission}. Voici les faits : {u_input}"
        resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        out = resp.choices[0].message.content
        
        conn = sqlite3.connect('legalos_v2.db')
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO dossiers VALUES (?,?)", (st.session_state.current_dossier, st.session_state.user_email))
        c.execute("INSERT OR REPLACE INTO steps VALUES (?,?,?,?,?,0)", (st.session_state.user_email, st.session_state.current_dossier, idx, u_input, out))
        conn.commit()
        conn.close()
        st.session_state.last_out = out
        st.rerun()

with col2:
    st.subheader("Conseil de Kareem")
    txt = st.session_state.get("last_out", a_db)
    if txt:
        if "last_out" in st.session_state:
            typewriter(txt)
            del st.session_state.last_out
        else:
            st.markdown(f'<div class="kareem-card">{txt}</div>', unsafe_allow_html=True)

# BOUTON DE VALIDATION AVEC SAUT AUTOMATIQUE
if a_db and not val_db:
    st.divider()
    if st.button("✅ VALIDER ET PASSER À L'ÉTAPE SUIVANTE"):
        conn = sqlite3.connect('legalos_v2.db')
        c = conn.cursor()
        c.execute("UPDATE steps SET validated=1 WHERE user_email=? AND dossier_nom=? AND step_idx=?", (st.session_state.user_email, st.session_state.current_dossier, idx))
        conn.commit()
        conn.close()
        
        # LOGIQUE DE SAUT : On incrémente l'index
        if st.session_state.current_step_idx < 11:
            st.session_state.current_step_idx += 1
            st.success(f"Étape {idx} validée ! Passage à l'étape {idx + 1}...")
            time.sleep(1)
            st.rerun()
        else:
            st.success("Dossier terminé !")
