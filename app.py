import streamlit as st
import pandas as pd
import os
from logic.router import qualifier_le_dossier
from logic.tools.reader import extraire_texte_pdf, extraire_dates_cles
from logic.tools.analyzer import analyser_validite_juridique
from logic.tools.chatbot import reponse_chat_juridique_stream

# 1. CONFIGURATION
st.set_page_config(page_title="Fortas OS", layout="wide", page_icon="⚖️")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; background-color: #1E3A8A; color: white; font-weight: bold; }
    .stChatMessage { border-radius: 15px; }
    .diag-result { background-color: #f0f7ff; padding: 20px; border-radius: 10px; border-left: 5px solid #1E3A8A; }
    .advice-card { background-color: #fff9db; padding: 15px; border-radius: 10px; border: 1px dashed #f08c00; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. INITIALISATION
if "messages" not in st.session_state: st.session_state.messages = []
if "branche_active" not in st.session_state: st.session_state.branche_active = None
if "analyse_gpt" not in st.session_state: st.session_state.analyse_gpt = ""
if "conseils_automatiques" not in st.session_state: st.session_state.conseils_automatiques = ""

# 3. NAVIGATION
st.sidebar.title("⚖️ Fortas OS")
etapes = ["1. Qualification", "2. Chronologie", "3. Validité", "4. Inventaire", "5. Calculs"]
choix_etape = st.sidebar.radio("Navigation :", etapes)

st.title(f"📍 {choix_etape}")

# --- ÉTAPE 1 : LE DUO STRATÉGIQUE ---
if "1. Qualification" in choix_etape:
    col_g, col_d = st.columns([1, 1], gap="large")

    with col_g:
        st.subheader("🧠 GPT Interne : Analyse Stratégique")
        faits = st.text_area("Saisissez les faits :", height=250, placeholder="Décrivez le dossier ici...", key="input_faits")
        
        if st.button("🚀 Lancer l'Analyse Complète"):
            if faits:
                with st.spinner("Génération de la stratégie..."):
                    # 1. L'IA analyse les faits
                    res = qualifier_le_dossier(faits)
                    st.session_state.branche_active = res['branche']
                    st.session_state.analyse_gpt = res['message']
                    
                    # 2. AUTOMATISATION : On demande au bot d'extraire les conseils immédiatement
                    with st.spinner("Extraction des conseils de procédure..."):
                        # On crée un prompt invisible pour extraire les conseils
                        prompt_conseils = f"Basé sur cette analyse : {res['message']}, extrais : 1. Les articles de loi clés, 2. Les délais de prescription, 3. Trois conseils pratiques pour l'avocat."
                        # On récupère la réponse (on simule un stream pour l'expérience utilisateur)
                        generateur = reponse_chat_juridique_stream(prompt_conseils, [])
                        st.session_state.conseils_automatiques = "".join(list(generateur))
            else:
                st.warning("Veuillez saisir des faits.")

        if st.session_state.analyse_gpt:
            st.markdown(f"""<div class="diag-result"><h4>📝 Analyse Stratégique</h4>{st.session_state.analyse_gpt}</div>""", unsafe_allow_html=True)

    with col_d:
        st.subheader("📚 Le Collaborateur : Fiche Pratique")
        
        if st.session_state.conseils_automatiques:
            st.markdown("### ⚡ Conseils Extraits Automatiquement")
            st.markdown(f"""<div class="advice-card">{st.session_state.conseils_automatiques}</div>""", unsafe_allow_html=True)
            
            st.divider()
            st.markdown("### 💬 Questions Complémentaires")
            
            # Container de chat pour approfondir
            chat_container = st.container(height=300)
            with chat_container:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]): st.markdown(message["content"])

            if prompt := st.chat_input("Besoin d'un modèle de clause ou d'un autre article ?"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with chat_container:
                    with st.chat_message("user"): st.markdown(prompt)
                    with st.chat_message("assistant"):
                        ctx = f"Analyse : {st.session_state.analyse_gpt}. Conseils déjà donnés : {st.session_state.conseils_automatiques}"
                        reponse = st.write_stream(reponse_chat_juridique_stream(f"Contexte: {ctx}\nQuestion: {prompt}", []))
                st.session_state.messages.append({"role": "assistant", "content": reponse})
        else:
            st.info("L'analyse à gauche générera automatiquement ici vos conseils et articles de loi.")

# --- AUTRES ÉTAPES ---
elif "2. Chronologie" in choix_etape:
    st.subheader("📅 Chronologie")
    st.info("Utilisez cette étape pour extraire les dates des pièces PDF.")

else:
    st.info(f"Module {choix_etape} prêt à recevoir les données de l'étape 1.")
