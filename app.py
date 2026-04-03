import streamlit as st
import sqlite3
import bcrypt
import time
from groq import Groq

# ---------------- CONFIG ----------------
# TA CLÉ RÉINSÉRÉE ICI
GROQ_KEY = "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"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="LegalOS V2 - Méthode Freeman", layout="wide")

# ---------------- DB ----------------
def init_db():
    conn = sqlite3.connect('legalos_v2.db')
    c = conn.cursor()
    # Utilisation de TEXT pour le mot de passe pour plus de simplicité avec SQLite/Bcrypt
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password TEXT,
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

# Initialisation immédiate
init_db()

# ---------------- AUTH ----------------
def login(e, p):
    try:
        conn = sqlite3.connect('legalos_v2.db')
        c = conn.cursor()
        c.execute("SELECT name, password FROM users WHERE email=?", (e,))
        res = c.fetchone()
        conn.close()
        if res:
            # Vérification robuste du hash
            stored_pw = res[1]
            if isinstance(stored_pw, str):
                stored_pw = stored_pw.encode()
            if bcrypt.checkpw(p.encode(), stored_pw):
                return res[0]
    except Exception as err:
        st.error(f"Erreur de login: {err}")
    return None

def register(e, p, n):
    conn = sqlite3.connect('legalos_v2.db')
    c = conn.cursor()
    hashed = bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode() # Decode pour stocker en TEXT
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (e, hashed, n))
        conn.commit()
        return True
    except Exception as err:
        st.error(f"Erreur d'inscription: {err}")
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
    font-family: 'Courier New', Courier, monospace;
    color: #10b981;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TYPEWRITER ----------------
def typewriter(text):
    container = st.empty()
    out = ""
    for char in text:
        out += char
        container.markdown(f'<div class="kareem-card">🤖 KAREEM IA :<br><br>{out}▌</div>', unsafe_allow_html=True)
        time.sleep(0.001)
    container.markdown(f'<div class="kareem-card">🤖 KAREEM IA :<br><br>{text}</div>', unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "auth" not in st.session_state:
    st.session_state.auth = False
if "page" not in st.session_state:
    st.session_state.page = "cabinet"

# ---------------- LOGIN PAGE ----------------
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>⚖️ LegalOS V2</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8;'>Système de Pilotage - Méthode Freeman</p>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Connexion", "Inscription"])

    with tab1:
        with st.form("login_form"):
            e = st.text_input("Email")
            p = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Se connecter au Cabinet"):
                name = login(e, p)
                if name:
                    st.session_state.auth = True
                    st.session_state.user_email = e
                    st.session_state.user_name = name
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")

    with tab2:
        with st.form("register_form"):
            n_reg = st.text_input("Nom complet")
            e_reg = st.text_input("Email")
            p_reg = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Créer mon accès"):
                if register(e_reg, p_reg, n_reg):
                    st.success("Compte créé avec succès ! Connectez-vous.")
                else:
                    st.error("Cet email est déjà utilisé.")
    st.stop()

# ---------------- CABINET (GESTION DOSSIERS) ----------------
if st.session_state.page == "cabinet":
    st.title(f"📂 Cabinet - {st.session_state.user_name}")
    
    if st.button("➕ Créer une nouvelle affaire Freeman"):
        st.session_state.current_dossier = f"Affaire_{int(time.time())}"
        # On insère le dossier immédiatement pour Kareem
        conn = sqlite3.connect('legalos_v2.db')
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO dossiers VALUES (?,?)", (st.session_state.current_dossier, st.session_state.user_email))
        conn.commit()
        conn.close()
        st.session_state.page = "work"
        st.rerun()

    st.subheader("Vos dossiers en cours :")
    conn = sqlite3.connect('legalos_v2.db')
    c = conn.cursor()
    c.execute("SELECT nom FROM dossiers WHERE user_email=?", (st.session_state.user_email,))
    dossiers = c.fetchall()
    conn.close()

    for d in dossiers:
        if st.button(f"📁 {d[0]}"):
            st.session_state.current_dossier = d[0]
            st.session_state.page = "work"
            st.rerun()
    
    if st.sidebar.button("Déconnexion"):
        st.session_state.auth = False
        st.rerun()
    st.stop()

# ---------------- WORKSPACE ----------------
steps = ["Qualification", "Objectif", "Base légale", "Inventaire", "Risques", "Amiable", "Stratégie", "Rédaction", "Audience", "Jugement", "Recours"]

with st.sidebar:
    st.title("⚖️ FREEMAN")
    st.write(f"Dossier : **{st.session_state.current_dossier}**")
    if st.button("⬅ Retour au Cabinet"):
        st.session_state.page = "cabinet"
        st.rerun()

    step_choice = st.radio("Étapes du dossier", steps)
    idx = steps.index(step_choice) + 1

st.title(f"💼 {step_choice}")

# ---------------- LOAD STEP DATA ----------------
conn = sqlite3.connect('legalos_v2.db')
c = conn.cursor()
c.execute("SELECT faits, analyse, validated FROM steps WHERE user_email=? AND dossier_nom=? AND step_idx=?",
          (st.session_state.user_email, st.session_state.current_dossier, idx))
row = c.fetchone()
conn.close()

faits_db, analyse_db, validated = row if row else ("", "", 0)

# ---------------- LOCK LOGIC ----------------
if idx > 1:
    conn = sqlite3.connect('legalos_v2.db')
    c = conn.cursor()
    c.execute("SELECT validated FROM steps WHERE user_email=? AND dossier_nom=? AND step_idx=?",
              (st.session_state.user_email, st.session_state.current_dossier, idx-1))
    prev = c.fetchone()
    conn.close()
    if not prev or prev[0] == 0:
        st.warning(f"⛔ L'étape {idx-1} doit être validée avant d'accéder à celle-ci.")
        st.stop()

# ---------------- INTERFACE TRAVAIL ----------------
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("📝 Matière brute")
    user_input = st.text_area("Notez les faits, documents ou réponses pour Kareem :", value=faits_db, height=350)

    if st.button("⚡ LANCER KAREEM (STRATÉGIE)"):
        # Context historique
        conn = sqlite3.connect('legalos_v2.db')
        c = conn.cursor()
        c.execute("SELECT step_idx, faits, analyse FROM steps WHERE user_email=? AND dossier_nom=? AND step_idx < ?",
                  (st.session_state.user_email, st.session_state.current_dossier, idx))
        rows = c.fetchall()
        conn.close()
        
        history = "\n".join([f"E{r[0]}: {r[1]} -> {r[2]}" for r in rows])
        
        missions = {
            1: "Détermine la qualification juridique exacte.",
            2: "Définis un objectif chiffré et clair.",
            3: "Liste les articles de loi et codes.",
            4: "Analyse les preuves fournies et liste les manquantes.",
            5: "Liste les risques et donne un score de réussite /100.",
            6: "Propose une stratégie de négociation amiable.",
            7: "AVOCAT DU DIABLE : Attaque ce dossier sans pitié pour trouver les failles.",
            8: "Rédige l'acte juridique (Assignation/Mise en demeure).",
            9: "Simule le Juge : Pose les questions qui font mal.",
            10: "Analyse le jugement rendu.",
            11: "Propose un recours (Appel/Cassation)."
        }

        prompt = f"Tu es Kareem, Directeur Juridique froid et expert.\n\nHISTORIQUE DU DOSSIER:\n{history}\n\nMISSION ACTUELLE (Etape {idx}): {missions[idx]}\n\nINPUT UTILISATEUR: {user_input}\n\nRéponds avec autorité, sois tranchant."

        with st.spinner("Kareem analyse..."):
            resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            output = resp.choices[0].message.content

        # Sauvegarde
        conn = sqlite3.connect('legalos_v2.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO steps VALUES (?,?,?,?,?,0)",
                  (st.session_state.user_email, st.session_state.current_dossier, idx, user_input, output))
        conn.commit()
        conn.close()
        st.session_state.last_ia = output
        st.rerun()

with col2:
    st.subheader("🤖 Rapport Kareem")
    final_text = st.session_state.get("last_ia", analyse_db)
    if final_text:
        if st.session_state.get("last_ia"): # Si on vient de cliquer sur le bouton
            typewriter(final_text)
            st.session_state.last_ia = None # Reset pour éviter de reboucler l'anim
        else:
            st.markdown(f'<div class="kareem-card">🤖 KAREEM IA :<br><br>{final_text}</div>', unsafe_allow_html=True)

if analyse_db and not validated:
    st.divider()
    if st.button("✅ VALIDER CETTE ÉTAPE ET PASSER À LA SUITE"):
        conn = sqlite3.connect('legalos_v2.db')
        c = conn.cursor()
        c.execute("UPDATE steps SET validated=1 WHERE user_email=? AND dossier_nom=? AND step_idx=?",
                  (st.session_state.user_email, st.session_state.current_dossier, idx))
        conn.commit()
        conn.close()
        st.success("Étape validée. Kareem vous attend à la suivante.")
        st.rerun()
