import streamlit as st

# 1. CONFIGURATION DE LA PAGE (Doit être la 1ère instruction)
st.set_page_config(
    page_title="LegalOS v1.0 - Reddington Protocol", 
    layout="wide", 
    page_icon="⚖️"
)

# 2. IMPORTATION DES VUES (Étapes)
from views.etape_1 import afficher_qualification
# On importe les étapes au fur et à mesure de leur création
try:
    from views.etape_2 import afficher_objectif
    from views.etape_3 import afficher_base_legale
    from views.etape_4 import afficher_preuves
except ImportError:
    # Fonctions de secours si les fichiers ne sont pas encore créés
    def afficher_objectif(): st.info("🎯 Étape 2 : En attente du fichier views/etape_2.py")
    def afficher_base_legale(): st.info("📚 Étape 3 : En attente du fichier views/etape_3.py")
    def afficher_preuves(): st.info("📁 Étape 4 : En attente du fichier views/etape_4.py")

# 3. DESIGN SYSTÈME (Dark Mode Professionnel)
st.markdown("""
    <style>
    /* Fond de l'application */
    .stApp { background-color: #0f172a; color: white; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { 
        background-color: #1e293b; 
        border-right: 1px solid #334155; 
    }
    
    /* Conteneur principal des étapes */
    .step-container {
        background-color: #1e293b;
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #334155;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }

    /* Override des textes Streamlit en blanc */
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {
        color: white !important;
    }

    /* Champs de saisie */
    .stTextArea textarea, .stTextInput input {
        background-color: #0f172a !important;
        color: white !important;
        border: 1px solid #334155 !important;
    }

    /* Boutons stylisés */
    .stButton>button {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white !important;
        border: none;
        font-weight: bold;
        padding: 0.6rem 1rem;
        transition: 0.3s;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

# 4. NAVIGATION : LES 11 ÉTAPES REDDINGTON
st.sidebar.title("🧠 LegalOS v1.0")
st.sidebar.caption("Protocole de gestion universel")
st.sidebar.markdown("---")

menu_reddington = {
    "1️⃣ Qualification": afficher_qualification,
    "2️⃣ Objectif": afficher_objectif,
    "3️⃣ Base légale": afficher_base_legale,
    "4️⃣ Preuves / Dossier": afficher_preuves,
    "5️⃣ Analyse stratégique": lambda: st.info("📈 Étape 5 : Évaluation des risques et probabilités."),
    "6️⃣ Phase amiable": lambda: st.info("🤝 Étape 6 : Stratégie de négociation et mise en demeure."),
    "7️⃣ Choix de procédure": lambda: st.info("⚖️ Étape 7 : Détermination de la juridiction compétente."),
    "8️⃣ Rédaction juridique": lambda: st.info("✍️ Étape 8 : Génération intelligente des actes."),
    "9️⃣ Audience": lambda: st.info("🗣️ Étape 9 : Préparation des arguments oraux."),
    "🔟 Jugement": lambda: st.info("🏛️ Étape 10 : Analyse du dispositif de la décision."),
    "1️⃣1️⃣ Exécution / Recours": lambda: st.info("🔄 Étape 11 : Mise en œuvre ou contestation.")
}

selection = st.sidebar.radio("Navigation du Protocole :", list(menu_reddington.keys()))

# 5. ZONE DE TITRE ET AFFICHAGE
st.title(f"📍 {selection}")

try:
    menu_reddington[selection]()
except Exception as e:
    st.error(f"Erreur d'affichage dans le module {selection} : {e}")

# 6. FOOTER SIDEBAR
st.sidebar.markdown("---")
if 'branche_active' in st.session_state:
    st.sidebar.write(f"📁 Dossier : **{st.session_state.branche_active}**")
    st.sidebar.write(f"🛡️ Procédure : **{st.session_state.get('cat_procedure', 'N/A')}**")
