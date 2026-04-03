import streamlit as st
import sqlite3
import bcrypt
import time
from groq import Groq

# ---------------- CONFIG ----------------
GROQ_KEY = "TA_CLE_API_ICI"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS V2", layout="wide")

# ---------------- DB ----------------
def init_db():
    conn = sqlite3.connect('legalos_v2.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password BLOB,
        name TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS dossiers (
        nom TEXT,
        user_email TEXT,
        PRIMARY KEY(nom, user_email)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS steps (
        user_email TEXT,
        dossier_nom TEXT,
        step_idx INTEGER,
        faits TEXT,
        analyse TEXT,
        validated INTEGER DEFAULT 0,
        PRIMARY KEY(user_email, dossier_nom, step_idx)
    )''')

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

    if res and bcrypt.checkpw(p.encode(), res[1]):
        return res[0]
    return None

def register(e, p, n):
    conn = sqlite3.connect('legalos_v2.db')
    c = conn.cursor()
    hashed = bcrypt.hashpw(p.encode(), bcrypt.gensalt())

    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (e, hashed, n))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
.stApp { background-color: #0b0f19; color: #e2e8f0; }
.kareem-card {
    background: #161b22;
    border-left: 5px solid #10b981;
    padding: 20px;
    border-radius: 10px;
    font-family: monospace;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TYPEWRITER ----------------
def typewriter(text):
    container = st.empty()
    out = ""
    for c in text:
        out += c
        container.markdown(f'<div class="kareem-card">🤖 {out}▌</div>', unsafe_allow_html=True)
        time.sleep(0.002)
    container.markdown(f'<div class="kareem-card">🤖 {text}</div>', unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "auth" not in st.session_state:
    st.session_state.auth = False

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.title("⚖️ LegalOS V2")

    tab1, tab2 = st.tabs(["Connexion", "Inscription"])

    with tab1:
        e = st.text_input("Email")
        p = st.text_input("Mot de passe", type="password")
        if st.button("Connexion"):
            name = login(e, p)
            if name:
                st.session_state.auth = True
                st.session_state.user_email = e
                st.session_state.user_name = name
                st.rerun()

    with tab2:
        n = st.text_input("Nom")
        e = st.text_input("Email ")
        p = st.text_input("Mot de passe ", type="password")
        if st.button("Créer compte"):
            if register(e, p, n):
                st.success("Compte créé")

    st.stop()

# ---------------- NAV ----------------
if "page" not in st.session_state:
    st.session_state.page = "cabinet"

# ---------------- CABINET ----------------
if st.session_state.page == "cabinet":
    st.title(f"📂 Dossiers - {st.session_state.user_name}")

    if st.button("➕ Nouvelle affaire"):
        st.session_state.current_dossier = f"Affaire_{int(time.time())}"
        st.session_state.page = "work"
        st.rerun()

    conn = sqlite3.connect('legalos_v2.db')
    c = conn.cursor()
    c.execute("SELECT nom FROM dossiers WHERE user_email=?", (st.session_state.user_email,))
    dossiers = c.fetchall()
    conn.close()

    for d in dossiers:
        if st.button(d[0]):
            st.session_state.current_dossier = d[0]
            st.session_state.page = "work"
            st.rerun()

    st.stop()

# ---------------- WORKSPACE ----------------
steps = [
    "Qualification", "Objectif", "Base légale", "Inventaire",
    "Risques", "Amiable", "Stratégie", "Rédaction",
    "Audience", "Jugement", "Recours"
]

with st.sidebar:
    st.title("⚖️ Freeman")
    if st.button("⬅ Retour"):
        st.session_state.page = "cabinet"
        st.rerun()

    step_choice = st.radio("Étapes", steps)
    idx = steps.index(step_choice) + 1

st.title(f"💼 {st.session_state.current_dossier}")

# ---------------- LOAD STEP ----------------
conn = sqlite3.connect('legalos_v2.db')
c = conn.cursor()

c.execute("""SELECT faits, analyse, validated FROM steps
WHERE user_email=? AND dossier_nom=? AND step_idx=?""",
          (st.session_state.user_email, st.session_state.current_dossier, idx))

row = c.fetchone()
conn.close()

faits_db, analyse_db, validated = row if row else ("", "", 0)

# ---------------- LOCK STEP ----------------
if idx > 1:
    conn = sqlite3.connect('legalos_v2.db')
    c = conn.cursor()
    c.execute("""SELECT validated FROM steps
    WHERE user_email=? AND dossier_nom=? AND step_idx=?""",
              (st.session_state.user_email, st.session_state.current_dossier, idx-1))
    prev = c.fetchone()
    conn.close()

    if not prev or prev[0] == 0:
        st.warning("⛔ Étape précédente non validée")
        st.stop()

# ---------------- INPUT ----------------
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Étape {idx} : {step_choice}")

    user_input = st.text_area("Input", value=faits_db, height=300)

    if st.button("⚡ LANCER L'ANALYSE STRATÉGIQUE"):

        # CONTEXTE STRUCTURÉ
        conn = sqlite3.connect('legalos_v2.db')
        c = conn.cursor()
        c.execute("""SELECT step_idx, faits, analyse FROM steps
        WHERE user_email=? AND dossier_nom=?""",
                  (st.session_state.user_email, st.session_state.current_dossier))

        history = ""
        for r in c.fetchall():
            history += f"\nÉtape {r[0]}:\nFaits: {r[1]}\nAnalyse: {r[2]}\n"

        conn.close()

        missions = {
            1: "Donne la qualification juridique précise.",
            2: "Définis un objectif chiffré.",
            3: "Liste les articles de loi.",
            4: "Analyse les preuves.",
            5: "Liste les risques + SCORE /100.",
            6: "Propose une négociation.",
            7: "Attaque le dossier.",
            8: "Rédige acte juridique.",
            9: "Simule juge.",
            10: "Analyse jugement.",
            11: "Propose recours."
        }

        prompt = f"""
Tu es Kareem, Directeur Juridique.

Tu décides.
Tu critiques.
Tu es froid et stratégique.

CONTEXTE :
{history}

MISSION :
{missions[idx]}

INPUT :
{user_input}

Réponse structurée obligatoire.
"""

        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        output = resp.choices[0].message.content

        conn = sqlite3.connect('legalos_v2.db')
        c = conn.cursor()

        c.execute("INSERT OR IGNORE INTO dossiers VALUES (?,?)",
                  (st.session_state.current_dossier, st.session_state.user_email))

        c.execute("""INSERT OR REPLACE INTO steps
        VALUES (?,?,?,?,?,0)""",
                  (st.session_state.user_email,
                   st.session_state.current_dossier,
                   idx,
                   user_input,
                   output))

        conn.commit()
        conn.close()

        st.session_state.last = output
        st.rerun()

# ---------------- OUTPUT ----------------
with col2:
    st.subheader("Analyse Kareem")

    text = st.session_state.get("last", analyse_db)

    if text:
        typewriter(text)

# ---------------- VALIDATION ----------------
if analyse_db and not validated:
    if st.button("✅ Valider étape"):
        conn = sqlite3.connect('legalos_v2.db')
        c = conn.cursor()
        c.execute("""UPDATE steps SET validated=1
        WHERE user_email=? AND dossier_nom=? AND step_idx=?""",
                  (st.session_state.user_email,
                   st.session_state.current_dossier,
                   idx))
        conn.commit()
        conn.close()
        st.success("Étape validée")
        st.rerun()
