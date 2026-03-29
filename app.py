import streamlit as st
from views.etape_1 import afficher_qualification
from views.etape_2 import afficher_objectif
from views.etape_3 import afficher_base_legale
from views.etape_4 import afficher_preuves
from views.etape_5 import afficher_strategie
from views.etape_6 import afficher_amiable
from views.etape_7 import afficher_choix_procedure
from views.etape_8 import afficher_redaction
from views.etape_9 import afficher_audience
from views.etape_10 import afficher_jugement
from views.etape_11 import afficher_recours

# 1. CONFIGURATION (Doit être la toute première ligne)
st.set_page_config(page_title="LegalOS v1.0", layout="wide", page_icon="⚖️")

# 2. INITIALISATION DE LA MÉMOIRE (Session State)
# On s'assure que les variables existent pour éviter les erreurs d'import
if 'branche_active' not in st.session_state:
    st.session_state.branche_active = "Non définie"
if 'cat_procedure' not in st.session_state:
    st.session_state.cat_procedure = "En attente d'analyse"
if 'objectif_final' not in st.session_state:
    st.session_state.objectif_final = None

# 3. DESIGN SYSTÈME (Dark Mode & Professional UI)
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: white; }
    [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    .step-container { 
        background-color: #1e293b; 
        padding: 25px; 
        border-radius: 12px; 
        border: 1px solid #334155;
    }
    h1, h2, h3, p, span, label { color: white !important; }
    .stButton>button { 
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); 
        color: white !important; 
        font-weight: bold; 
        width: 100%; 
        border: none;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. SIDEBAR - NAVIGATION & RÉSUMÉ DU DOSSIER
st.sidebar.title("🧠 LegalOS v1.0")
st.sidebar.caption("Protocole Reddington Universel")
st.sidebar.markdown("---")

# Menu de navigation
menu_reddington = {
    "1️⃣ Qualification": afficher_qualification,
    "2️⃣ Objectif": afficher_objectif,
    "3️⃣ Base légale": afficher_base_legale,
    "4️⃣ Preuves / Dossier": afficher_preuves,
    "5️⃣ Analyse stratégique": afficher_strategie,
    "6️⃣ Phase amiable": afficher_amiable,
    "7️⃣ Choix de procédure": afficher_choix_procedure,
    "8️⃣ Rédaction juridique": afficher_redaction,
    "9️⃣ Audience": afficher_audience,
    "🔟 Jugement": afficher_jugement,
    "1️⃣1️⃣ Exécution / Recours": afficher_recours
}

selection = st.sidebar.radio("Navigation du Protocole :", list(menu_reddington.keys()))

# --- RÉSUMÉ DYNAMIQUE DANS LA SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.subheader("📋 État du Dossier")
st.sidebar.write(f"📂 Branche : **{st.session_state.branche_active}**")
st.sidebar.write(f"🛡️ Type : **{st.session_state.cat_procedure}**")

if st.session_state.objectif_final:
    st.sidebar.success(f"🎯 Objectif : \n{st.session_state.objectif_final}")
    if st.session_state.get('montant_estime', 0) > 0:
        st.sidebar.write(f"💰 Enjeu : **{st.session_state.montant_estime} €**")

# 5. AFFICHAGE DE LA PAGE SÉLECTIONNÉE
st.title(f"📍 {selection}")

# Exécution de la fonction associée à la sélection
menu_reddington[selection]()

# 6. FOOTER
st.sidebar.markdown("---")
st.sidebar.caption("Système sécurisé v1.0.26")
