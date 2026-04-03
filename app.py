import streamlit as st
import sqlite3
import bcrypt
import time
import PyPDF2
from groq import Groq

# ---------------- CONFIGURATION GROQ ----------------
GROQ_KEY = "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"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS - Freeman 11 Steps", layout="wide")

# ---------------- INITIALISATION BASE DE DONNÉES ----------------
def init_db():
    conn = sqlite3.connect('legalos_v11.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT, name TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS dossiers (nom TEXT, user_email TEXT, PRIMARY KEY(nom, user_email))')
    c.execute('CREATE TABLE IF NOT EXISTS steps (user_email TEXT, dossier_nom TEXT, step_idx INTEGER, faits TEXT, analyse TEXT, validated INTEGER DEFAULT 0, PRIMARY KEY(user_email, dossier_nom, step_idx))')
    conn.commit()
    conn.close()

init_db()

# ---------------- EFFET MACHINE À ÉCRIRE (RYTHME LÉGAL) ----------------
def typewriter(text, speed=0.005):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(f'<div style="background:#161b22; padding:20px; border-left:5px solid #10b981; border-radius:10px; font-family:monospace; color:#e2e8f0; line-height:1.6;"><b>🤖 KAREEM :</b><br><br>{full_text}▌</div>', unsafe_allow_html=True)
        time.sleep(speed)
    container.markdown(f'<div style="background:#161b22; padding:20px; border-left:5px solid #10b981; border-radius:10px; font-family:monospace; color:#e2e8f0; line-height:1.6;"><b>🤖 KAREEM :</b><br><br>{text}</div>', unsafe_allow_html=True)

# ---------------- AUTHENTIFICATION ----------------
if "auth" not in st.session_state: st.session_state.auth = False
if "current_step_idx" not in st.session_state: st.session_state.current_step_idx = 1

if not st.session_state.auth:
    st.title("⚖️ LegalOS - Freeman Method")
    with st.form("login"):
        e = st.text_input("Email")
        p = st.text_input("Mot de passe", type="password")
        if st.form_submit_button("Entrer au Cabinet"):
            st.session_state.auth, st.session_state.user_email = True, e
            st.rerun()
    st.stop()

# ---------------- GESTION DES DOSSIERS ----------------
if "page" not in st.session_state: st.session_state.page = "cabinet"

if st.session_state.page == "cabinet":
    st.title("📂 Cabinet de Pilotage Stratégique")
    if st.button("➕ NOUVEAU DOSSIER FREEMAN"):
        st.session_state.current_dossier = f"Dossier_{int(time.time())}"
        st.session_state.page, st.session_state.current_step_idx = "work", 1
        st.rerun()
    
    conn = sqlite3.connect('legalos_v11.db')
    c = conn.cursor()
    c.execute("SELECT nom FROM dossiers WHERE user_email=?", (st.session_state.user_email,))
    for d in c.fetchall():
        if st.button(f"📁 {d[0]}", use_container_width=True):
            st.session_state.current_dossier, st.session_state.page = d[0], "work"
            st.rerun()
    st.stop()

# ---------------- LES 11 ÉTAPES DE LA MÉTHODE ----------------
steps_titles = [
    "1. Qualification (Le Diagnostic)",
    "2. Objectif (Le Gain visé)",
    "3. Base Légale (La Loi)",
    "4. Inventaire (Les Preuves PDF)",
    "5. Analyse des Risques (Avocat du Diable)",
    "6. Stratégie Amiable (Négociation)",
    "7. Plan d'Attaque (Tactique)",
    "8. Rédaction (Mise en demeure/Actes)",
    "9. Audience (Préparation)",
    "10. Jugement (Analyse de décision)",
    "11. Recours (Suites à donner)"
]

with st.sidebar:
    st.header("MÉTHODE FREEMAN")
    if st.button("⬅ Cabinet"): st.session_state.page = "cabinet"; st.rerun()
    choice = st.radio("Séquence :", steps_titles, index=st.session_state.current_step_idx - 1)
    st.session_state.current_step_idx = steps_titles.index(choice) + 1
    idx = st.session_state.current_step_idx

st.title(f"💼 {st.session_state.current_dossier}")
st.subheader(choice)

# --- CHARGEMENT HISTORIQUE (POUR LA MÉMOIRE DE KAREEM) ---
conn = sqlite3.connect('legalos_v11.db')
c = conn.cursor()
c.execute("SELECT step_idx, analyse FROM steps WHERE user_email=? AND dossier_nom=? AND step_idx < ?", 
          (st.session_state.user_email, st.session_state.current_dossier, idx))
history = "\n".join([f"E{r[0]}: {r[1]}" for r in c.fetchall()])

# --- CHARGEMENT ÉTAPE ACTUELLE ---
c.execute("SELECT faits, analyse, validated FROM steps WHERE user_email=? AND dossier_nom=? AND step_idx=?", 
          (st.session_state.user_email, st.session_state.current_dossier, idx))
row = c.fetchone()
conn.close()
f_db, a_db, v_db = row if row else ("", "", 0)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.write("### 📥 Saisie & Documents")
    
    # MODULE LECTURE PDF (Spécifique Etape 4 mais disponible partout si besoin)
    pdf_text = ""
    if idx == 4:
        file = st.file_uploader("Scanner de preuves (PDF)", type="pdf")
        if file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages: pdf_text += page.extract_text()
            st.success("Preuves ingérées par Kareem.")

    u_input = st.text_area("Notes complémentaires ou éléments de fait :", value=f_db, height=350)
    
    if st.button("⚡ EXECUTER KAREEM"):
        with st.spinner("Kareem traite les données..."):
            instructions = {
                1: "Qualifie juridiquement les faits. Identifie les infractions ou manquements.",
                2: "Définis l'objectif final. Que voulons-nous obtenir précisément ?",
                3: "Cite les articles de loi, codes et jurisprudence applicables.",
                4: "Analyse les documents PDF fournis et confronte-les à la base légale de l'étape 3.",
                5: "Fais l'analyse critique : quels sont les points faibles de notre dossier ?",
                6: "Propose un protocole d'accord transactionnel ou une phase amiable.",
                7: "Établis la chronologie tactique du dossier.",
                8: "Rédige la structure argumentative de la mise en demeure ou de l'acte.",
                9: "Prépare les éléments de langage pour l'audience.",
                10: "Analyse le résultat obtenu et les motifs du juge.",
                11: "Détermine s'il faut faire appel ou exécuter la décision."
            }
            
            prompt = f"""
            Tu es Kareem, Directeur Juridique expert de la méthode Freeman.
            HISTORIQUE DU DOSSIER : {history}
            MISSION ÉTAPE {idx} ({choice}) : {instructions.get(idx)}
            SAISIE/DOCS : {u_input} {pdf_text}
            Donne une analyse directive, structurée et sans fioritures.
            """
            
            resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            out = resp.choices[0].message.content
            
            # SAUVEGARDE
            conn = sqlite3.connect('legalos_v11.db')
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO dossiers VALUES (?,?)", (st.session_state.current_dossier, st.session_state.user_email))
            c.execute("INSERT OR REPLACE INTO steps VALUES (?,?,?,?,?,0)", (st.session_state.user_email, st.session_state.current_dossier, idx, u_input, out))
            conn.commit(); conn.close()
            
            st.session_state.type_trigger = out
            st.rerun()

with col2:
    st.write("### 🤖 Décision de Kareem")
    final_txt = st.session_state.get("type_trigger", a_db)
    if final_txt:
        if "type_trigger" in st.session_state:
            typewriter(final_txt)
            del st.session_state.type_trigger
        else:
            st.markdown(f'<div style="background:#161b22; padding:20px; border-left:5px solid #10b981; border-radius:10px; font-family:monospace; color:#e2e8f0; line-height:1.6;">{final_txt}</div>', unsafe_allow_html=True)

# --- VALIDATION POUR PASSER À LA SUITE ---
if a_db and not v_db:
    st.divider()
    if st.button(f"✅ VALIDER ET PASSER À L'ÉTAPE SUIVANTE"):
        conn = sqlite3.connect('legalos_v11.db')
        c = conn.cursor()
        c.execute("UPDATE steps SET validated=1 WHERE user_email=? AND dossier_nom=? AND step_idx=?", 
                  (st.session_state.user_email, st.session_state.current_dossier, idx))
        conn.commit(); conn.close()
        
        if st.session_state.current_step_idx < len(steps_titles):
            st.session_state.current_step_idx += 1
            st.rerun()
        else:
            st.balloons()
            st.success("Dossier Freeman complété !")
