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

st.set_page_config(page_title="LegalOS v1.0", layout="wide", page_icon="⚖️")

# DESIGN (Identique à ta version sombre)
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: white; }
    [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    .step-container { background-color: #1e293b; padding: 25px; border-radius: 12px; border: 1px solid #334155; }
    h1, h2, h3, p, span, label { color: white !important; }
    .stButton>button { background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); color: white !important; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("🧠 LegalOS v1.0")
st.sidebar.markdown("---")

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

selection = st.sidebar.radio("Protocole Reddington :", list(menu_reddington.keys()))
st.title(f"📍 {selection}")

menu_reddington[selection]()
