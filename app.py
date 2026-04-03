import streamlit as st
import sqlite3
import bcrypt
import time
import PyPDF2
from groq import Groq

# ---------------- CONFIG ----------------
GROQ_KEY = "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"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS V4 - Pilotage Kareem", layout="wide")

# ---------------- DB ----------------
def init_db():
    conn = sqlite3.connect('legalos_v4.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT, name TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS dossiers (nom TEXT, user_email TEXT, PRIMARY KEY(nom, user_email))')
    c.execute('CREATE TABLE IF NOT EXISTS steps (user_email TEXT, dossier_nom TEXT, step_idx INTEGER, faits TEXT, analyse TEXT, validated INTEGER DEFAULT 0, PRIMARY KEY(user_email, dossier_nom, step_idx))')
    conn.commit()
    conn.close()

init_db()

# ---------------- LOGIQUE KAREEM (LE LEAD) ----------------
def kareem_take_control(dossier, email, base_facts):
    """Kareem génère toute la colonne vertébrale du dossier dès l'étape 1."""
    prompt = f"""
    Tu es Kareem, Directeur Juridique. Basé sur ces faits : {base_facts}, 
    prépare immédiatement la stratégie Freeman.
    Génère 3 blocs distincts séparés par '---' :
    1. OBJECTIF (E2) : Quel est le résultat financier/juridique visé ?
    2. BASE LÉGALE (E3) : Quels codes et articles ?
    3. RISQUES (E5) : Pourquoi on pourrait échouer ?
    Sois bref et autoritaire.
    """
    try:
        resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        full_plan = resp.choices[0].message.content
        parts = full_plan.split('---')
        
        conn = sqlite3.connect('legalos_v4.db')
        c = conn.cursor()
        # Pré-remplissage des étapes 2, 3 et 5
        indices = [2, 3, 5]
        for i, idx in enumerate(indices):
            content = parts[i].strip() if i < len(parts) else "Analyse en attente..."
            c.execute("INSERT OR REPLACE INTO steps (user_email, dossier_nom, step_idx, faits, analyse, validated) VALUES (?,?,?,?,?,0)", 
                      (email, dossier, idx, "Généré par anticipation", content))
        conn.commit()
        conn.close()
    except: pass

# ---------------- INTERFACE ----------------
if "auth" not in st.session_state: st.session_state.auth = False
if "current_step_idx" not in st.session_state: st.session_state.current_step_idx = 1

# AUTH SIMPLIFIÉE POUR ÉVITER LES BLOCAGES
if not st.session_state.auth:
    st.title("⚖️ LegalOS V4")
    with st.form("auth_f"):
        e = st.text_input("Email")
        p = st.text_input("Pass", type="password")
        if st.form_submit_button("Entrer"):
            st.session_state.auth, st.session_state.user_email = True, e
            st.rerun()
    st.stop()

# CABINET
if "page" not in st.session_state: st.session_state.page = "cabinet"
if st.session_state.page == "cabinet":
    st.title("📂 Vos Dossiers")
    if st.button("➕ NOUVEAU DOSSIER"):
        st.session_state.current_dossier = f"Affaire_{int(time.time())}"
        st.session_state.page, st.session_state.current_step_idx = "work", 1
        st.rerun()
    # Liste des dossiers
    conn = sqlite3.connect('legalos_v4.db')
    c = conn.cursor()
    c.execute("SELECT nom FROM dossiers WHERE user_email=?", (st.session_state.user_email,))
    for d in c.fetchall():
        if st.button(f"📁 {d[0]}"):
            st.session_state.current_dossier, st.session_state.page = d[0], "work"
            st.rerun()
    st.stop()

# WORKSPACE
steps = ["1. Qualification", "2. Objectif", "3. Base légale", "4. Inventaire (DOCS)", "5. Risques", "6. Amiable", "7. Stratégie", "8. Rédaction", "9. Audience", "10. Jugement", "11. Recours"]
with st.sidebar:
    if st.button("⬅ Retour"): st.session_state.page = "cabinet"; st.rerun()
    choice = st.radio("Séquence Freeman", steps, index=st.session_state.current_step_idx - 1)
    st.session_state.current_step_idx = steps.index(choice) + 1
    idx = st.session_state.current_step_idx

st.title(f"💼 {st.session_state.current_dossier}")
st.header(choice)

# Load DB
conn = sqlite3.connect('legalos_v4.db')
c = conn.cursor()
c.execute("SELECT faits, analyse, validated FROM steps WHERE user_email=? AND dossier_nom=? AND step_idx=?", (st.session_state.user_email, st.session_state.current_dossier, idx))
row = c.fetchone()
conn.close()
f_db, a_db, v_db = row if row else ("", "", 0)

col1, col2 = st.columns(2)

with col1:
    # SI ÉTAPE 4 : ACTIVATION DU SCANNER
    pdf_text = ""
    if idx == 4:
        st.subheader("📁 SCANNER DE DOCUMENTS")
        file = st.file_uploader("Déposez le contrat ou la preuve (PDF)", type="pdf")
        if file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages: pdf_text += page.extract_text()
            st.success("Document intégré à l'analyse de Kareem.")

    u_input = st.text_area("Notes ou Faits :", value=f_db, height=300)
    
    if st.button("⚡ EXECUTER KAREEM"):
        context = u_input + ("\nDOCS: " + pdf_text if pdf_text else "")
        prompt = f"Tu es Kareem (Lead). Etape {idx}. Analyse et décide : {context}"
        resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
        out = resp.choices[0].message.content
        
        conn = sqlite3.connect('legalos_v4.db')
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO dossiers VALUES (?,?)", (st.session_state.current_dossier, st.session_state.user_email))
        c.execute("INSERT OR REPLACE INTO steps VALUES (?,?,?,?,?,0)", (st.session_state.user_email, st.session_state.current_dossier, idx, u_input, out))
        conn.commit()
        st.session_state.last_ia = out
        st.rerun()

with col2:
    st.subheader("🤖 DECISION KAREEM")
    res_display = st.session_state.get("last_ia", a_db)
    if res_display:
        st.markdown(f'<div style="background:#161b22; padding:20px; border-left:5px solid #10b981; border-radius:10px; color:#10b981; font-family:monospace;">{res_display}</div>', unsafe_allow_html=True)

# BOUTON VALIDATION (QUI DÉCLENCHE L'ANTICIPATION)
if a_db and not v_db:
    st.divider()
    if st.button("✅ VALIDER & LANCER L'ANTICIPATION"):
        if idx == 1:
            with st.spinner("Kareem prépare les étapes suivantes..."):
                kareem_take_control(st.session_state.current_dossier, st.session_state.user_email, u_input)
        
        conn = sqlite3.connect('legalos_v4.db')
        c = conn.cursor()
        c.execute("UPDATE steps SET validated=1 WHERE user_email=? AND dossier_nom=? AND step_idx=?", (st.session_state.user_email, st.session_state.current_dossier, idx))
        conn.commit()
        
        if st.session_state.current_step_idx < 11:
            st.session_state.current_step_idx += 1
            st.rerun()
