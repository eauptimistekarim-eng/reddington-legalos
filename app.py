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
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.warning("⚠️ Configuration : Clé API Groq manquante dans les Secrets Streamlit.")
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
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "RAPPORT LEGALOS - SYSTEME FREEMAN", ln=True, align='C')
        pdf.ln(10)
        for i in range(11):
            if st.session_state.data[i]:
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, f"ETAPE {i+1}: {STEPS[i]}", ln=True)
                pdf.set_font("Arial", '', 10)
                pdf.multi_cell(0, 5, f"NOTES : {st.session_state.data[i]}")
                if st.session_state.ai_reports[i]:
                    pdf.set_font("Arial", 'I', 10)
                    pdf.multi_cell(0, 5, f"ANALYSE KAREEM : {st.session_state.ai_reports[i]}")
                pdf.ln(5)
        return pdf.output(dest='S').encode('latin-1', 'replace')
    except:
        return None

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
                st.error("Code incorrect.")

# --- DASHBOARD PRINCIPAL ---
else:
    with st.sidebar:
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

    st.markdown(f"<h2 class='step-header'>Étape {st.session_state.step + 1} : {STEPS[st.session_state.step]}</h2>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1.8, 1.2])
    
    with col_left:
        input_text = st.text_area("Saisissez vos éléments...", value=st.session_state.data[st.session_state.step], height=300)
        st.session_state.data[st.session_state.step] = input_text
        
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("🚀 LANCER L'ANALYSE KAREEM"):
                if client and len(input_text) > 10:
                    with st.spinner("Kareem analyse votre dossier..."):
                        try:
                            # Utilisation du modèle le plus récent et stable
                            p = f"Tu es Kareem, expert juridique méthode Freeman. Analyse l'étape {STEPS[st.session_state.step]} pour : {input_text}"
                            resp = client.chat.completions.create(
                                messages=[{"role": "user", "content": p}],
                                model="llama-3.3-70b-versatile",
                            )
                            st.session_state.ai_reports[st.session_state.step] = resp.choices[0].message.content
                            st.rerun()
                        except Exception as e:
                            st.error("L'IA est saturée. Réessayez dans quelques secondes.")
                            st.info(f"Détail technique : {e}")
                else:
                    st.warning("Texte trop court.")
        
        with c_btn2:
            if st.button("ÉTAPE SUIVANTE ➔"):
                if st.session_state.step < 10:
                    st.session_state.step += 1
                    st.rerun()

    with col_right:
        st.markdown("### 🤖 RÉPONSE DE KAREEM")
        if st.session_state.ai_reports[st.session_state.step]:
            st.markdown(f'<div class="kareem-box">{st.session_state.ai_reports[st.session_state.step]}</div>', unsafe_allow_html=True)
            
            pdf_data = export_as_pdf()
            if pdf_data:
                st.download_button("📥 Télécharger le Dossier PDF", pdf_data, "dossier_legalos.pdf", "application/pdf")
        else:
            st.info("En attente d'analyse.")

st.caption("LegalOS v2.1 - Reddington Protocol")
