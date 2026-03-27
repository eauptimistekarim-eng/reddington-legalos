import streamlit as st
from groq import Groq
from fpdf import FPDF

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Reddington LegalOS", layout="wide", initial_sidebar_state="expanded")

# --- INITIALISATION GROQ ---
# Ta clé est intégrée ici directement
client = Groq(api_key="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")

# --- FONCTION GÉNÉRATION PDF ---
def generate_pdf(text_red, text_devil):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="RAPPORT DE STRATÉGIE REDDINGTON", ln=True, align='C')
    pdf.ln(10)
    
    # Section Reddington
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(200, 10, txt="1. ANALYSE STRATEGIQUE (LES 11 ETAPES)", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)
    # Nettoyage des caractères spéciaux pour le PDF
    clean_red = text_red.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 5, txt=clean_red)
    
    pdf.ln(10)
    
    # Section Avocat du Diable
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(229, 62, 62)
    pdf.cell(200, 10, txt="2. ANALYSE DE L'AVOCAT DU DIABLE", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)
    clean_devil = text_devil.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 5, txt=clean_devil)
    
    return pdf.output(dest='S').encode('latin-1')

# --- STYLE CSS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3.5em; background-color: #1a365d; color: white; font-weight: bold; }
    .report-box { padding: 20px; border-radius: 10px; border-left: 5px solid #1a365d; background-color: white; margin-bottom: 20px; font-family: 'Helvetica'; }
    .devil-box { padding: 20px; border-radius: 10px; border-left: 5px solid #e53e3e; background-color: #fff5f5; font-family: 'Helvetica'; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("⚖️ Méthode Reddington")
steps = [
    "1. Faits", "2. Qualification", "3. Preuves", "4. Intentions", 
    "5. Scan Procédure", "6. Avocat du Diable", "7. Riposte", 
    "8. Risques", "9. Action", "10. Rédaction", "11. Suivi"
]
for step in steps:
    st.sidebar.write(f"🔹 {step}")

st.sidebar.markdown("---")
st.sidebar.info("**Standard LegalOS v1.0** - Connecté à Groq LPU")

# --- CORPS DE L'APPLICATION ---
st.title("🛡️ Reddington LegalOS")
st.markdown("##### *Anticiper. Analyser. Riposter.*")

cas_juridique = st.text_area(
    "Détaillez votre cas juridique ici :", 
    height=200, 
    placeholder="Décrivez les faits, les dates et les acteurs impliqués..."
)

col1, col2 = st.columns([2, 1])

if st.button("LANCER L'ANALYSE DE COMBAT"):
    if not cas_juridique:
        st.warning("Veuillez saisir des informations avant l'analyse.")
    else:
        with st.spinner("Analyse en cours via Groq (300ms/token)..."):
            
            # PROMPT REDDINGTON
            prompt_red = f"""
            Tu es Reddington, expert en procédure française. Analyse ce cas selon tes 11 étapes. 
            Cite les codes (CPC, CPP, Travail). Sois chirurgical.
            CAS : {cas_juridique}
            """
            
            # PROMPT AVOCAT DU DIABLE
            prompt_dev = f"""
            Tu es l'Avocat du Diable. Ton but est de détruire le dossier de l'utilisateur. 
            Trouve les failles, les mensonges potentiels et les faiblesses de preuve.
            CAS : {cas_juridique}
            """

            try:
                # Appels API
                res_red = client.chat.completions.create(model="llama3-70b-8192", messages=[{"role": "user", "content": prompt_red}], temperature=0.1)
                res_dev = client.chat.completions.create(model="llama3-70b-8192", messages=[{"role": "user", "content": prompt_dev}], temperature=0.7)

                # Stockage des résultats
                txt_red = res_red.choices[0].message.content
                txt_dev = res_dev.choices[0].message.content

                with col1:
                    st.markdown("### 📜 Stratégie Reddington")
                    st.markdown(f'<div class="report-box">{txt_red}</div>', unsafe_allow_html=True)

                with col2:
                    st.markdown("### 👹 L'Avocat du Diable")
                    st.markdown(f'<div class="devil-box">{txt_dev}</div>', unsafe_allow_html=True)
                    
                    st.markdown("---")
                    # Bouton PDF
                    pdf_bytes = generate_pdf(txt_red, txt_dev)
                    st.download_button(
                        label="📥 Télécharger le Dossier (PDF)",
                        data=pdf_bytes,
                        file_name="strategie_reddington.pdf",
                        mime="application/pdf"
                    )

            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")

st.markdown("---")
st.caption("Usage professionnel uniquement. Reddington LegalOS ne remplace pas un avocat assermenté.")
