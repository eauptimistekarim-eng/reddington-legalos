import streamlit as st
import sqlite3
import bcrypt
import time
import PyPDF2
from groq import Groq

# ---------------- CONFIG ----------------
GROQ_KEY = "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"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS - Freeman", layout="wide")

# ---------------- DB ----------------
def init_db():
    conn = sqlite3.connect('legalos_ultra_v4.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT, name TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS dossiers (nom TEXT, user_email TEXT, PRIMARY KEY(nom, user_email))')
    c.execute('CREATE TABLE IF NOT EXISTS steps (user_email TEXT, dossier_nom TEXT, step_idx INTEGER, faits TEXT, analyse TEXT, validated INTEGER DEFAULT 0, PRIMARY KEY(user_email, dossier_nom, step_idx))')
    conn.commit()
    conn.close()

init_db()

# ---------------- EFFET MACHINE À ÉCRIRE ----------------
def typewriter(text, speed=0.005):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(f'<div style="background:#161b22; padding:20px; border-left:5px solid #10b981; border-radius:10px; font-family:monospace; color:#e2e8f0; line-height:1.5;"><b>🤖 KAREEM :</b><br><br>{full_text}▌</div>', unsafe_allow_html=True)
        time.sleep(speed)
    container.markdown(f'<div style="background:#161b22; padding:20px; border-left:5px solid #10b981; border-radius:10px; font-family:monospace; color:#e2e8f0; line-height:1.5;"><b>🤖 KAREEM :</b><br><br>{text}</div>', unsafe_allow_html=True)

# ---------------- LOGIQUE DE DÉCOUPAGE ----------------
def dispatch_kareem_logic(dossier, email, raw_ai_text):
    """Découpe la réponse de l'IA et remplit les étapes futures."""
    conn = sqlite3.connect('legalos_ultra_v4.db')
    c = conn.cursor()
    
    # On cherche les balises [E2], [E3], etc.
    mapping = {"[E2]": 2, "[E3]": 3, "[E5]": 5, "[E7]": 7, "[E8]": 8}
    
    for tag, idx in mapping.items():
        if tag in raw_ai_text:
            # Extraction du texte entre cette balise et la suivante (ou la fin)
            part = raw_ai_text.split(tag)[1]
            for other_tag in mapping.keys():
                part = part.split(other_tag)[0]
            
            clean_content = part.strip().replace("---", "")
            c.execute("INSERT OR REPLACE INTO steps (user_email, dossier_nom, step_idx, faits, analyse, validated) VALUES (?,?,?,?,?,0)", 
                      (email, dossier, idx, "Anticipation Kareem", clean_content))
    
    conn.commit()
    conn.close()

# ---------------- AUTH & SESSION ----------------
if "auth" not in st.session_state: st.session_state.auth = False
if "current_step_idx" not in st.session_state: st.session_state.current_step_idx = 1

if not st.session_state.auth:
    st.title("⚖️ LegalOS - Méthode Freeman")
    with st.form("login"):
        e = st.text_input("Email")
        p = st.text_input("Mot de passe", type="password")
        if st.form_submit_button("Entrer au Cabinet"):
            st.session_state.auth, st.session_state.user_email = True, e
            st.rerun()
    st.stop()

if "page" not in st.session_state: st.session_state.page = "cabinet"

# --- CABINET ---
if st.session_state.page == "cabinet":
    st.title("📂 Gestion des Affaires")
    if st.button("➕ NOUVEAU DOSSIER"):
        st.session_state.current_dossier = f"Affaire_{int(time.time())}"
        st.session_state.page, st.session_state.current_step_idx = "work", 1
        st.rerun()
    
    conn = sqlite3.connect('legalos_ultra_v4.db')
    c = conn.cursor()
    c.execute("SELECT nom FROM dossiers WHERE user_email=?", (st.session_state.user_email,))
    for d in c.fetchall():
        if st.button(f"📁 {d[0]}", use_container_width=True):
            st.session_state.current_dossier, st.session_state.page = d[0], "work"
            st.rerun()
    st.stop()

# --- ESPACE DE TRAVAIL ---
steps = ["1. Qualification", "2. Objectif", "3. Base légale", "4. Inventaire (DOCS)", "5. Risques", "6. Amiable", "7. Stratégie", "8. Rédaction", "9. Audience", "10. Jugement", "11. Recours"]

with st.sidebar:
    st.header("MÉTHODE FREEMAN")
    if st.button("⬅ Cabinet"): st.session_state.page = "cabinet"; st.rerun()
    choice = st.radio("Séquence", steps, index=st.session_state.current_step_idx - 1)
    st.session_state.current_step_idx = steps.index(choice) + 1
    idx = st.session_state.current_step_idx

st.title(f"💼 {st.session_state.current_dossier}")
st.subheader(choice)

# Load data
conn = sqlite3.connect('legalos_ultra_v4.db')
c = conn.cursor()
c.execute("SELECT faits, analyse, validated FROM steps WHERE user_email=? AND dossier_nom=? AND step_idx=?", (st.session_state.user_email, st.session_state.current_dossier, idx))
row = c.fetchone()
conn.close()
f_db, a_db, v_db = row if row else ("", "", 0)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.write("### 🖋️ Saisie")
    pdf_txt = ""
    if idx == 4:
        f = st.file_uploader("Scanner PDF", type="pdf")
        if f:
            reader = PyPDF2.PdfReader(f)
            for p in reader.pages: pdf_txt += p.extract_text()
            st.success("Document lu.")

    u_input = st.text_area("Faits / Notes :", value=f_db, height=350)
    
    if st.button("⚡ EXECUTER KAREEM"):
        with st.spinner("Kareem réfléchit..."):
            prompt = f"""
            Tu es Kareem. Etape {idx}. Contexte: {u_input}. Docs: {pdf_txt}.
            Si c'est l'étape 1, génère AUSSI le futur sous ces balises : 
            [E2] Objectif financier... [E3] Articles de loi... [E5] Risques...
            """
            resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            out = resp.choices[0].message.content
            
            # Sauvegarde et Découpage
            conn = sqlite3.connect('legalos_ultra_v4.db')
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO dossiers VALUES (?,?)", (st.session_state.current_dossier, st.session_state.user_email))
            c.execute("INSERT OR REPLACE INTO steps VALUES (?,?,?,?,?,0)", (st.session_state.user_email, st.session_state.current_dossier, idx, u_input, out))
            conn.commit()
            conn.close()
            
            if idx == 1: dispatch_kareem_logic(st.session_state.current_dossier, st.session_state.user_email, out)
            
            st.session_state.trigger_typewriter = out
            st.rerun()

with col2:
    st.write("### 🤖 Kareem IA")
    res = st.session_state.get("trigger_typewriter", a_db)
    if res:
        if "trigger_typewriter" in st.session_state:
            typewriter(res)
            del st.session_state.trigger_typewriter
        else:
            st.markdown(f'<div style="background:#161b22; padding:20px; border-left:5px solid #10b981; border-radius:10px; font-family:monospace; color:#e2e8f0;">{res}</div>', unsafe_allow_html=True)

if a_db and not v_db:
    if st.button("✅ VALIDER & CONTINUER"):
        conn = sqlite3.connect('legalos_ultra_v4.db')
        c = conn.cursor()
        c.execute("UPDATE steps SET validated=1 WHERE user_email=? AND dossier_nom=? AND step_idx=?", (st.session_state.user_email, st.session_state.current_dossier, idx))
        conn.commit(); conn.close()
        if st.session_state.current_step_idx < 11:
            st.session_state.current_step_idx += 1
            st.rerun()
