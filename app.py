import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="LegalOS - Kareem IA", page_icon="⚖️", layout="wide")

# --- STYLE PERSONNALISÉ ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; }
    .kareem-box { background-color: #1e293b; color: white; padding: 20px; border-radius: 15px; border-left: 5px solid #10b981; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DES DONNÉES ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'data' not in st.session_state:
    st.session_state.data = {i: "" for i in range(11)}

STEPS = ["Qualification", "Objectif", "Base légale", "Preuves", "Analyse", "Amiable", "Procédure", "Rédaction", "Audience", "Jugement", "Recours"]
VALID_CODES = ["FREEMAN2026", "VIP_LEGAL", "TEST01"]

# --- ÉCRAN DE CONNEXION ---
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("⚖️ LegalOS")
        st.subheader("Accès Système Freeman")
        code = st.text_input("Entrez votre code VIP", type="password")
        if st.button("ACTIVER KAREEM IA"):
            if code.upper() in VALID_CODES:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Code invalide")

# --- DASHBOARD PRINCIPAL ---
else:
    with st.sidebar:
        st.title("KAREEM IA")
        st.write("---")
        for i, s in enumerate(STEPS):
            if st.button(f"{i+1}. {s}", key=f"btn_{i}"):
                st.session_state.step = i
                st.rerun()
        if st.button("Se déconnecter"):
            st.session_state.auth = False
            st.rerun()

    # Zone de travail
    st.header(f"Étape {st.session_state.step + 1} : {STEPS[st.session_state.step]}")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        user_text = st.text_area("Saisissez les détails pour Kareem...", 
                                value=st.session_state.data[st.session_state.step], 
                                height=300)
        st.session_state.data[st.session_state.step] = user_text
        
        uploaded_file = st.file_uploader("Ajouter des pièces jointes (PDF, Images...)", accept_multiple_files=True)
        
        if st.button("LANCER L'ANALYSE"):
            st.success("Analyse en cours par Kareem...")
            # Ici on pourra ajouter la logique Groq/IA plus tard

    with col_right:
        st.markdown(f"""
        <div class="kareem-box">
            <small style="color: #10b981;">KAREEM IA ANALYSE</small><br><br>
            Prêt pour l'étape <b>{STEPS[st.session_state.step]}</b>.<br><br>
            <i>"Donnez-moi les faits, je m'occupe du droit."</i>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.step < 10:
            if st.button("ÉTAPE SUIVANTE ➔"):
                st.session_state.step += 1
                st.rerun()

st.info("Version Bêta - Système Reddington")
