import streamlit as st
from groq import Groq
from fpdf import FPDF

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Reddington LegalOS", layout="wide", initial_sidebar_state="expanded")

# --- INITIALISATION GROQ (Modèle Llama 3.3 Mis à jour) ---
client = Groq(api_key="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")
MODEL_NAME = "llama-3.3-70b-versatile"

# --- FONCTION GÉNÉRATION PDF ---
def generate_pdf(text_red, text_devil):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="RAPPORT DE STRATEGIE REDDINGTON", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(200, 10, txt="1. ANALYSE STRATEGIQUE (REDDINGTON)", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)
    # Nettoyage pour éviter les erreurs d'encodage PDF
    clean_red = text_red.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 5, txt=clean_red)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(229, 62, 62)
    pdf.cell(200, 10, txt="2. L'AVOCAT DU DIABLE", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)
    clean_devil = text_devil.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 5, txt=clean_devil)
    
    return pdf.output(dest='S').encode('latin-1')

# --- STYLE CSS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #002b5b; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #004085; border: none; color: white; }
    .report-box { padding: 25px; border-radius: 12px; border-top: 6px solid #1a365d; background-color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 25px; color: #1a202c; }
    .devil-box { padding: 25px; border-radius: 12px; border-top: 6px solid #e53e3e; background-color: #fff5f5; box-shadow: 0 4px 6px rgba(0,0,0,0.1); color: #1a202c; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("Méthode Reddington")
steps = ["1. Faits", "2. Qualification", "3. Preuves", "4. Intentions", "5. Procédure", "6. Avocat du Diable", "7. Riposte", "8. Risques", "9. Action", "10. Rédaction", "11. Suivi"]
for step in steps:
    st.sidebar.write(f"⚖️ {step}")

# --- CORPS DE L'APPLICATION ---
st.title("🛡️ Reddington LegalOS")
st.markdown("##### *Intelligence Artificielle de Haute Stratégie Juridique*")
st.divider()

cas_juridique = st.text_area(
    "Exposez les faits de votre dossier :", 
    height=250, 
    placeholder="Soyez précis : dates, montants, échanges mails, clauses du contrat..."
)

col1, col2 = st.columns([1, 1])

if st.button("LANCER L'ANALYSE DE COMBAT"):
    if not cas_juridique:
        st.warning("⚠️ Merci d'entrer les détails du cas.")
    else:
        with st.spinner("🧠 Reddington analyse les failles..."):
            
            # PROMPTS
            prompt_red = f"Tu es Raymond Reddington, génie de la stratégie. Analyse ce cas juridique avec brio, précision chirurgicale et cite les lois françaises pertinentes. Utilise la méthode Reddington. CAS : {cas_juridique}"
            prompt_dev = f"Tu es l'Avocat du Diable. Ton but est de détruire les arguments de l'utilisateur. Trouve toutes les failles et les risques de perdre. CAS : {cas_juridique}"

            try:
                # Appels API
                res_red = client.chat.completions.create(model=MODEL_NAME, messages=[{"role": "user", "content": prompt_red}], temperature=0.1)
                res_dev = client.chat.completions.create(model=MODEL_NAME, messages=[{"role": "user", "content": prompt_dev}], temperature=0.7)

                txt_red = res_red.choices[0].message.content
                txt_dev = res_dev.choices[0].message.content

                with col1:
                    st.subheader("📜 Stratégie Reddington")
                    st.markdown(f'<div class="report-box">{txt_red}</div>', unsafe_allow_html=True)

                with col2:
                    st.subheader("👹 L'Avocat du Diable")
                    st.markdown(f'<div class="devil-box">{txt_dev}</div>', unsafe_allow_html=True)
                    
                    st.divider()
                    pdf_bytes = generate_pdf(txt_red, txt_dev)
                    st.download_button(
                        label="📥 Télécharger le Dossier (PDF)",
                        data=pdf_bytes,
                        file_name="strategie_reddington.pdf",
                        mime="application/pdf"
                    )

            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")

st.divider()
st.caption("Propulsé par Groq & Llama 3.3. Reddington LegalOS est un outil d'aide à la décision stratégique.")
