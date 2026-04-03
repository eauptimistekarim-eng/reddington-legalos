import streamlit as st
import sqlite3
import bcrypt
import time
from groq import Groq

# ---------------- CONFIGURATION ----------------
GROQ_KEY = "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"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS V2 - Freeman", layout="wide")

# ---------------- BASE DE DONNÉES ----------------
def init_db():
    conn = sqlite3.connect('legalos_v2.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT, name TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS dossiers (nom TEXT, user_email TEXT, PRIMARY KEY(nom, user_email))')
    c.execute('CREATE TABLE IF NOT EXISTS steps (user_email TEXT, dossier_nom TEXT, step_idx INTEGER, faits TEXT, analyse TEXT, validated INTEGER DEFAULT 0, PRIMARY KEY(user_email, dossier_nom, step_idx))')
    conn.commit()
    conn.close()

init_db()

# ---------------- FONCTIONS UTILES ----------------
def typewriter(text):
    container = st.empty()
    out = ""
    for char in text:
        out += char
        container.markdown(f'<div style="background:#161b22; padding:20px; border-left:5px solid #10b981; border-radius:10px; font-family:monospace; color:#e2e8f0;"><b>🤖 KAREEM :</b><br><br>{out}▌</div>', unsafe_allow_html=True)
        time.sleep(0.001)
    container.markdown(f'<div style="background:#161b22; padding:20px; border-left:5px solid #10b981; border-radius:10px; font-family:monospace; color:#e2e8f0;"><b>🤖 KAREEM :</b><br><br>{text}</div>', unsafe_allow_html=True)

# ---------------- ÉTAT DE LA SESSION ----------------
if "auth" not in st.session_state: st.session_state.auth = False
if "page" not in st.session_state: st.session_state.page = "cabinet"
if "current_step_idx" not in st.session_state: st.session_state.current_step_idx = 1

# ---------------- CONNEXION / INSCRIPTION ----------------
if not st.session_state.auth:
    st.title("⚖️ LegalOS V2")
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        with st.form("login"):
            e = st.text_input("Email")
            p = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Accéder au Cabinet"):
                conn = sqlite3.connect('legalos_v2.db')
                c = conn.cursor()
                c.execute("SELECT name, password FROM users WHERE email=?", (e,))
                res = c.fetchone()
                conn.close()
                if res and bcrypt.checkpw(p.encode(), res[1].encode() if isinstance(res[1], str) else res[1]):
                    st.session_state.auth, st.session_state.user_email, st.session_state.user_name = True, e, res[0]
                    st.rerun()
                else: st.error("Identifiants invalides.")
    with t2:
        with st.form("reg"):
            n_r, e_r, p_r = st.text_input("Nom"), st.text_input("Email"), st.text_input("Mdp", type="password")
            if st.form_submit_button("Créer compte"):
                h = bcrypt.hashpw(p_r.encode(), bcrypt.gensalt()).decode()
                try:
                    conn = sqlite3.connect('legalos_v2.db')
                    c.execute("INSERT INTO users VALUES (?, ?, ?)", (e_r, h, n_r))
                    conn.commit(); conn.close()
                    st.success("Compte créé, connectez-vous !")
                except: st.error("Email déjà pris.")
    st.stop()

# ---------------- CABINET ----------------
if st.session_state.page == "cabinet":
    st.title(f"📂 Cabinet - Me {st.session_state.user_name}")
    if st.button("➕ NOUVELLE AFFAIRE"):
        st.session_state.current_dossier = f"Affaire_{int(time.time())}"
        st.session_state.page, st.session_state.current_step_idx = "work", 1
        st.rerun()

    conn = sqlite3.connect('legalos_v2.db')
    c = conn.cursor()
    c.execute("SELECT nom FROM dossiers WHERE user_email=?", (st.session_state.user_email,))
    dossiers = c.fetchall()
    conn.close()
    for d in dossiers:
        if st.button(f"📁 {d[0]}", use_container_width=True):
            st.session_state.current_dossier, st.session_state.page = d[0], "work"
            st.rerun()
    st.stop()

# ---------------- ZONE DE TRAVAIL (ESPACE DE RÉDACTION) ----------------
steps = ["Qualification", "Objectif", "Base légale", "Inventaire", "Risques", "Amiable", "Stratégie", "Rédaction", "Audience", "Jugement", "Recours"]

with st.sidebar:
    st.header("MÉTHODE FREEMAN")
    if st.button("⬅ Cabinet"): st.session_state.page = "cabinet"; st.rerun()
    choice = st.radio("Étapes", steps, index=st.session_state.current_step_idx - 1)
    st.session_state.current_step_idx = steps.index(choice) + 1
    idx = st.session_state.current_step_idx

st.title(f"💼 {st.session_state.current_dossier}")
st.subheader(f"Étape {idx} : {choice}")

# Charger data existante
conn = sqlite3.connect('legalos_v2.db')
c = conn.cursor()
c.execute("SELECT faits, analyse, validated FROM steps WHERE user_email=? AND dossier_nom=? AND step_idx=?", (st.session_state.user_email, st.session_state.current_dossier, idx))
row = c.fetchone()
conn.close()
f_db, a_db, v_db = row if row else ("", "", 0)

# INTERFACE À DEUX COLONNES (Saisie / Kareem)
col1, col2 = st.columns(2, gap="large")

with col1:
    st.write("### 🖋️ Votre saisie")
    u_input = st.text_area("Décrivez les faits ou apportez vos éléments ici :", value=f_db, height=400)
    
    if st.button("⚡ ANALYSE KAREEM"):
        # Récupération historique
        conn = sqlite3.connect('legalos_v2.db')
        c = conn.cursor()
        c.execute("SELECT step_idx, analyse FROM steps WHERE user_email=? AND dossier_nom=? AND step_idx < ?", (st.session_state.user_email, st.session_state.current_dossier, idx))
        history = "\n".join([f"E{r[0]}: {r[1]}" for r in c.fetchall()])
        conn.close()

        prompt = f"Tu es Kareem, expert Freeman. Historique: {history}. Mission Etape {idx} ({choice}). Faits: {u_input}. Sois directif."
        
        resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        out = resp.choices[0].message.content
        
        # Sauvegarde
        conn = sqlite3.connect('legalos_v2.db')
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO dossiers VALUES (?,?)", (st.session_state.current_dossier, st.session_state.user_email))
        c.execute("INSERT OR REPLACE INTO steps (user_email, dossier_nom, step_idx, faits, analyse, validated) VALUES (?,?,?,?,?,0)", (st.session_state.user_email, st.session_state.current_dossier, idx, u_input, out))
        conn.commit(); conn.close()
        
        st.session_state.temp_out = out
        st.rerun()

with col2:
    st.write("### 🤖 Conseil de Kareem")
    display_text = st.session_state.get("temp_out", a_db)
    if display_text:
        if "temp_out" in st.session_state:
            typewriter(display_text)
            del st.session_state.temp_out
        else:
            st.markdown(f'<div style="background:#161b22; padding:20px; border-left:5px solid #10b981; border-radius:10px; font-family:monospace; color:#e2e8f0;"><b>🤖 KAREEM :</b><br><br>{display_text}</div>', unsafe_allow_html=True)

# VALIDATION ET SAUT AUTOMATIQUE
if a_db and not v_db:
    st.divider()
    if st.button("✅ VALIDER ET PASSER À L'ÉTAPE SUIVANTE"):
        conn = sqlite3.connect('legalos_v2.db')
        c = conn.cursor()
        c.execute("UPDATE steps SET validated=1 WHERE user_email=? AND dossier_nom=? AND step_idx=?", (st.session_state.user_email, st.session_state.current_dossier, idx))
        conn.commit(); conn.close()
        
        if st.session_state.current_step_idx < 11:
            st.session_state.current_step_idx += 1
            st.rerun()
