import streamlit as st
from groq import Groq
from fpdf import FPDF
import io

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="LegalOS - Kareem IA", page_icon="⚖️", layout="wide")

# --- STYLE PERSONNALISÉ (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 3em; transition: 0.3s; }
    .stButton>button:hover { background-color: #10b981; color: white; border: none; }
    .kareem-box { background-color: #1e293b; color: white; padding: 25px; border-radius: 15px; border-left: 6px solid #10b981; line-height: 1.6; }
    .step-header { color: #1e293b; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DU CLIENT GROQ ---
try:
    # Utilise st.secrets pour le déploiement Streamlit Cloud
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    # Message d'erreur si la clé est absente (utile pour VS Code)
    st.warning("⚠️ Clé API Groq non configurée. Ajoutez-la dans les Secrets de Streamlit.")
    client = None

# --- GESTION DE LA SESSION ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'step' not in st.session_state: st.session_state.step = 0
if 'data' not in st.session_state: st.session_state.data = {i: "" for i in range(11)}
if 'ai_reports' not in st.session_state: st.session_state.ai_reports = {i: "" for i in range(11)}

STEPS = [
    "Qualification des Faits", "Définition de l'Objectif", "Base Légale & Jurisprudence", 
    "Inventaire des Preuves", "Analyse des Risques", "Tentative Amiable", 
    "Stratégie de Procédure", "Rédaction des Actes", "Préparation Audience", 
    "Suivi du Jugement", "Voies de Recours"
]
VALID_CODES = ["FREEMAN2026", "VIP_LEGAL"]

# --- FONCTION GÉNÉRATION PDF ---
def export_as_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "RAPPORT LEGALOS - SYSTEME FREEMAN", ln=True, align='C')
    pdf.ln(10)
    
    for i in range(11):
        if st.session_state.data[i]:
            pdf.set_font("Arial", 'B', 12)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(0, 10, f"ETAPE {i+1}: {STEPS[i]}", ln=True, fill=True)
            pdf.ln(2)
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(0, 5, f"NOTES UTILISATEUR :\n{st.session_state.data[i]}")
            pdf.ln(2)
            if st.session_state.ai_reports[i]:
                pdf.set_font("Arial", 'I', 10)
                pdf.set_text_color(16, 185, 129)
                pdf.multi_cell(0, 5, f"ANALYSE KAREEM IA :\n{st.session_state.ai_reports[i]}")
                pdf.set_text_color(0, 0, 0)
            pdf.ln(5)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- ÉCRAN DE CONNEXION ---
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("⚖️ LegalOS")
        st.subheader("Accès Sécurisé - Méthode Freeman")
        code_input = st.text_input("Entrez votre code d'accès", type="password")
        if st.button("ACTIVER LE SYSTÈME"):
            if code_input.upper() in VALID_CODES:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Code incorrect. Accès refusé.")

# --- DASHBOARD PRINCIPAL ---
else:
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/1048/1048953.png", width=100)
        st.title("KAREEM IA")
        st.write("---")
        for i, s in enumerate(STEPS):
            label = f"✅ {i+1}. {s}" if st.session_state.ai_reports[i] else f"{i+1}. {s}"
            if st.button(label, key=f"side_{i}"):
                st.session_state.step = i
                st.rerun()
        
        st.write("---")
        if st.button("🚪 Déconnexion"):
            st.session_state.auth = False
            st.rerun()

    # Zone de Travail
    st.markdown(f"<h2 class='step-header'>Étape {st.session_state.step + 1} : {STEPS[st.session_state.step]}</h2>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1.8, 1.2])
    
    with col_left:
        # Zone de saisie
        input_text = st.text_area(
            "Détaillez les éléments de cette étape pour analyse...", 
            value=st.session_state.data[st.session_state.step], 
            height=350,
            help="Plus vous donnez de détails, plus l'analyse de Kareem sera précise."
        )
        st.session_state.data[st.session_state.step] = input_text
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚀 LANCER L'ANALYSE KAREEM"):
                if client and len(input_text) > 15:
                    with st.spinner("Kareem analyse les éléments
