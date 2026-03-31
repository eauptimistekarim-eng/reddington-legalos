import streamlit as st
import time
from groq import Groq
# On importe nos fonctions depuis le fichier processor.py (qui doit être dans le même dossier)
from processor import extract_text_from_pdf, get_freeman_prompt

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="LegalOS - Kareem IA", page_icon="⚖️", layout="wide")

# Style CSS pour l'interface "Dark Mode" et la boîte de réponse de l'IA
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: white; }
    .kareem-box { 
        background-color: #1e293b; 
        color: #f8fafc; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 5px solid #10b981; 
        font-size: 1.1rem;
        margin-top: 10px;
    }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #10b981; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- CONNEXION À L'IA (GROQ) ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    client = None
    st.warning("⚠️ Clé API Groq manquante dans les secrets.")

# --- ÉTAPES DE LA MÉTHODE FREEMAN ---
STEPS = ["Qualification", "Objectif", "Base Légale", "Preuves", "Risques", "Amiable", "Procédure", "Actes", "Audience", "Jugement", "Recours"]

# --- INITIALISATION DES VARIABLES DE SESSION ---
if 'step' not in st.session_state: st.session_state.step = 0
if 'data' not in st.session_state: st.session_state.data = {i: "" for i in range(len(STEPS))}
if 'ai_reports' not in st.session_state: st.session_state.ai_reports = {i: "" for i in range(len(STEPS))}

# --- FONCTION EFFET MACHINE À ÉCRIRE ---
def typewriter_effect(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(f'<div class="kareem-box">{full_text}▌</div>', unsafe_allow_html=True)
        time.sleep(0.005)
    container.markdown(f'<div class="kareem-box">{full_text}</div>', unsafe_allow_html=True)

# --- INTERFACE PRINCIPALE ---
st.title(f"⚖️ LegalOS - Étape {st.session_state.step + 1} : {STEPS[st.session_state.step]}")

# CRÉATION DES COLONNES (C'est ici que l'erreur est corrigée !)
col_left, col_right = st.columns([1.5, 1.5])

with col_left:
    st.subheader("📁 Dossier & Documents")
    
    # Zone d'upload PDF
    uploaded_file = st.file_uploader("Glissez votre document juridique (PDF)", type="pdf")
    if uploaded_file:
        with st.spinner("Extraction du texte..."):
            extracted_text = extract_text_from_pdf(uploaded_file)
            st.session_state.data[st.session_state.step] = extracted_text[:4000] # Limite pour l'IA
            st.success("Analyse du PDF terminée !")

    # Zone de texte manuelle
    user_input = st.text_area("Notes ou faits du dossier :", 
                              value=st.session_state.data[st.session_state.step], 
                              height=300)
    st.session_state.data[st.session_state.step] = user_input

    # Bouton d'analyse
    if st.button("🚀 LANCER L'ANALYSE KAREEM"):
        if not user_input:
            st.error("Veuillez entrer du texte ou un PDF.")
        elif client is None:
            st.error("L'IA n'est pas configurée (Clé API).")
        else:
            with st.spinner("Kareem analyse votre dossier..."):
                prompt = get_freeman_prompt(STEPS[st.session_state.step], user_input)
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                    )
                    st.session_state.ai_reports[st.session_state.step] = chat_completion.choices[0].message.content
                except Exception as e:
                    st.error(f"Erreur IA : {e}")

with col_right:
    st.subheader("🤖 Analyse de l'IA")
    if st.session_state.ai_reports[st.session_state.step]:
        # On affiche le résultat stocké
        st.markdown(f'<div class="kareem-box">{st.session_state.ai_reports[st.session_state.step]}</div>', unsafe_allow_html=True)
    else:
        st.info("En attente de l'analyse... Cliquez sur le bouton à gauche.")

# --- NAVIGATION ---
st.divider()
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    if st.button("⬅️ Étape Précédente") and st.session_state.step > 0:
        st.session_state.step -= 1
        st.rerun()
with c3:
    if st.button("Étape Suivante ➡️") and st.session_state.step < len(STEPS) - 1:
        st.session_state.step += 1
        st.rerun()
