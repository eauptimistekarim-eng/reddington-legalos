import streamlit as st
import sqlite3
import bcrypt
import time
import PyPDF2
import io
from groq import Groq

# ---------------- CONFIG ----------------
GROQ_KEY = "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"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS V3 - Freeman", layout="wide")

# ---------------- DB ----------------
def init_db():
    conn = sqlite3.connect('legalos_v3.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT, name TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS dossiers (nom TEXT, user_email TEXT, PRIMARY KEY(nom, user_email))')
    c.execute('CREATE TABLE IF NOT EXISTS steps (user_email TEXT, dossier_nom TEXT, step_idx INTEGER, faits TEXT, analyse TEXT, validated INTEGER DEFAULT 0, PRIMARY KEY(user_email, dossier_nom, step_idx))')
    conn.commit()
    conn.close()

init_db()

# ---------------- FONCTIONS IA & DOCS ----------------
def typewriter(text):
    container = st.empty()
    out = ""
    for char in text:
        out += char
        container.markdown(f'<div style="background:#161b22; padding:20px; border-left:5px solid #10b981; border-radius:10px; font-family:monospace; color:#e2e8f0;"><b>🤖 KAREEM :</b><br><br>{out}▌</div>', unsafe_allow_html=True)
        time.sleep(0.001)
    container.markdown(f'<div style="background:#161b22; padding:20px; border-left:5px solid #10b981; border-radius:10px; font-family:monospace; color:#e2e8f0;"><b>🤖 KAREEM :</b><br><br>{text}</div>', unsafe_allow_html=True)

def prefill_steps(dossier_nom, user_email, base_facts):
    """Kareem anticipe les étapes 2 et 3 dès la validation de la 1."""
    prompt = f"Basé sur ces faits : {base_facts}. Génère uniquement pour l'ÉTAPE 2 (Objectif chiffré) et l'ÉTAPE 3 (Articles de loi probables). Format: ETAPE2: [contenu] | ETAPE3: [contenu]"
    resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
    res = resp.choices[0].message.content
    
    # Parsing simple (à améliorer selon le format de l'IA)
    try:
        e2 = res.split("ETAPE2:")[1].split("|")[0].strip()
        e3 = res.split("ETAPE3:")[1].strip()
        conn = sqlite3.connect('legalos_v3.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO steps (user_email, dossier_nom, step_idx, faits, analyse, validated) VALUES (?,?,?,?,?,0)", (user_email, dossier_nom, 2, "Pré-rempli par Kareem", e2, 0))
        c.execute("INSERT OR REPLACE INTO steps (user_email, dossier_nom, step_idx, faits, analyse, validated) VALUES (?,?,?,?,?,0)", (user_email, dossier_nom, 3, "Pré-rempli par Kareem", e3, 0))
        conn.commit()
        conn.close()
    except: pass

# ---------------- SESSION ----------------
if "auth" not in st.session_state: st.session_state.auth = False
if "page" not in st.session_state: st.session_state.page = "cabinet"
if "current_step_idx" not in st.session_state: st.session_state.current_step_idx = 1

# ---------------- AUTH (Simplifiée pour la démo) ----------------
if not st.session_state.auth:
    st.title("⚖️ LegalOS V3 - Freeman")
    with st.form("login"):
        e = st.text_input("Email")
        p = st.text_input("Mdp", type="password")
        if st.form_submit_button("Entrer"):
            st.session_state.auth, st.session_state.user_email, st.session_state.user_name = True, e, "Utilisateur"
            st.rerun()
    st.stop()

# ---------------- CABINET ----------------
if st.session_state.page == "cabinet":
    st.title("📂 Vos Affaires")
    if st.button("➕ NOUVEAU DOSSIER"):
        st.session_state.current_dossier = f"Affaire_{int(time.time())}"
        st.session_state.page, st.session_state.current_step_idx = "work", 1
        st.rerun()
    
    conn = sqlite3.connect('legalos_v3.db')
    c = conn.cursor()
    c.execute("SELECT nom FROM dossiers WHERE user_email=?", (st.session_state.user_email,))
    for d in c.fetchall():
        if st.button(f"📁 {d[0]}", use_container_width=True):
            st.session_state.current_dossier, st.session_state.page = d[0], "work"
            st.rerun()
    st.stop()

# ---------------- WORKSPACE ----------------
steps = ["1. Qualification", "2. Objectif", "3. Base légale", "4. Inventaire (DOCS)", "5. Risques", "6. Amiable", "7. Stratégie", "8. Rédaction", "9. Audience", "10. Jugement", "11. Recours"]

with st.sidebar:
    if st.button("⬅ Cabinet"): st.session_state.page = "cabinet"; st.rerun()
    choice = st.radio("Méthode Freeman", steps, index=st.session_state.current_step_idx - 1)
    st.session_state.current_step_idx = steps.index(choice) + 1
    idx = st.session_state.current_step_idx

st.title(f"💼 {st.session_state.current_dossier}")
st.subheader(choice)

# Load data
conn = sqlite3.connect('legalos_v3.db')
c = conn.cursor()
c.execute("SELECT faits, analyse, validated FROM steps WHERE user_email=? AND dossier_nom=? AND step_idx=?", (st.session_state.user_email, st.session_state.current_dossier, idx))
row = c.fetchone()
conn.close()
f_db, a_db, v_db = row if row else ("", "", 0)

col1, col2 = st.columns(2, gap="large")

with col1:
    # OPTION SPÉCIALE ÉTAPE 4 : LECTURE DE PDF
    doc_context = ""
    if idx == 4:
        st.info("📂 Mode Inventaire : Téléchargez vos pièces jointes.")
        uploaded_file = st.file_uploader("Ajouter un document PDF", type="pdf")
        if uploaded_file:
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                doc_context += page.extract_text()
            st.success("Document lu avec succès par Kareem.")

    u_input = st.text_area("Saisie manuelle :", value=f_db, height=300)
    
    if st.button("⚡ LANCER KAREEM"):
        final_input = u_input + "\nCONTENU DOCUMENT: " + doc_context
        prompt = f"Tu es Kareem. Etape {idx}. Contexte: {final_input}. Sois chirurgical."
        
        resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        out = resp.choices[0].message.content
        
        conn = sqlite3.connect('legalos_v3.db')
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO dossiers VALUES (?,?)", (st.session_state.current_dossier, st.session_state.user_email))
        c.execute("INSERT OR REPLACE INTO steps VALUES (?,?,?,?,?,0)", (st.session_state.user_email, st.session_state.current_dossier, idx, u_input, out))
        conn.commit(); conn.close()
        st.session_state.temp_out = out
        st.rerun()

with col2:
    display = st.session_state.get("temp_out", a_db)
    if display:
        if "temp_out" in st.session_state:
            typewriter(display)
            del st.session_state.temp_out
        else:
            st.markdown(f'<div style="background:#161b22; padding:20px; border-left:5px solid #10b981; border-radius:10px; font-family:monospace; color:#e2e8f0;">{display}</div>', unsafe_allow_html=True)

if a_db and not v_db:
    if st.button("✅ VALIDER ET AUTOMATISER LA SUITE"):
        if idx == 1:
            prefill_steps(st.session_state.current_dossier, st.session_state.user_email, u_input)
        
        conn = sqlite3.connect('legalos_v3.db')
        c = conn.cursor(); c.execute("UPDATE steps SET validated=1 WHERE user_email=? AND dossier_nom=? AND step_idx=?", (st.session_state.user_email, st.session_state.current_dossier, idx))
        conn.commit(); conn.close()
        
        if st.session_state.current_step_idx < 11:
            st.session_state.current_step_idx += 1
            st.rerun()
