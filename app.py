import streamlit as st
import pandas as pd
import os
from logic.router import qualifier_le_dossier
from logic.tools.reader import extraire_texte_pdf, extraire_dates_cles
from logic.tools.analyzer import analyser_validite_juridique
from logic.tools.chatbot import reponse_chat_juridique_stream

# 1. CONFIGURATION ET DESIGN
st.set_page_config(page_title="Fortas OS", layout="wide", page_icon="⚖️")

st.markdown("""
    <style>
    /* Fond de page et boutons */
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        background-color: #1E3A8A; 
        color: white; 
        font-weight: bold;
        height: 3em;
    }
    /* Fixer la hauteur des zones pour éviter le défilement de page */
    .fixed-container {
        height: 450px;
        overflow-y: auto;
        padding: 15px;
        border: 1px solid #e6e9ef;
        border-radius: 10px;
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INITIALISATION DE LA MÉMOIRE
if "messages" not in st.session_state:
    st.session_state.messages = []
if "branche_active" not in st.session_state:
    st.session_state.branche_active = "Droit général"

# 3. BARRE LATÉRALE
st.sidebar.title("⚖️ Fortas OS")
etapes = ["1. Qualification", "2. Chronologie", "3. Validité", "4. Inventaire", "5. Calculs"]
choix_etape = st.sidebar.radio("Navigation :", etapes)

# 4. LOGIQUE DES ÉTAPES
st.title(f"📍 {choix_etape}")

# --- ÉTAPE 1 : QUALIFICATION & CONVERSATION ---
if "1. Qualification" in choix_etape:
    col_g, col_d = st.columns([1, 1], gap="large")

    with col_g:
        st.subheader("🧪 Analyse Poussée")
        # On utilise un container à hauteur fixe pour les faits
        faits = st.text_area("Exposez les faits bruts du dossier :", height=300, key="faits_zone")
        
        if st.button("Lancer le Diagnostic"):
            if faits:
                with st.spinner("Analyse technique..."):
                    res = qualifier_le_dossier(faits)
                    st.session_state['branche_active'] = res['branche']
                    st.success(f"Branche : {res['branche']}")
                    st.info(res['message'])
            else:
                st.warning("Veuillez saisir des faits.")

    with col_d:
        st.subheader("💬 Assistant Consultant")
        
        # ZONE DE CHAT FIXE (SCROLLABLE)
        # On utilise le paramètre height natif de st.container pour forcer le scroll
        chat_container = st.container(height=450)
        
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Saisie utilisateur (toujours collée en bas du container)
        if prompt := st.chat_input("Posez une question juridique..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    hist = [(m["content"], "") for m in st.session_state.messages if m["role"] == "user"]
                    reponse_complete = st.write_stream(reponse_chat_juridique_stream(prompt, hist))
            
            st.session_state.messages.append({"role": "assistant", "content": reponse_complete})

# --- ÉTAPE 2 : CHRONOLOGIE ---
elif "2. Chronologie" in choix_etape:
    st.subheader("📅 Chronologie & Lecture PDF")
    fichier = st.file_uploader("Déposez le document (PDF)", type="pdf")
    
    if st.button("🔍 Extraire les données"):
        if fichier:
            with st.spinner("Extraction..."):
                texte = extraire_texte_pdf(fichier)
                resultats = extraire_dates_cles(texte)
                st.session_state['donnees_du_pdf'] = resultats
                st.session_state['nom_fichier'] = fichier.name
                
                # Container fixe pour le tableau s'il est trop long
                with st.container(height=300):
                    if isinstance(resultats, list) and len(resultats) > 0:
                        st.table(pd.DataFrame(resultats))
                    else:
                        st.info("Aucune date détectée.")
                st.success("Données prêtes.")
        else:
            st.warning("Veuillez charger un fichier.")

# --- ÉTAPE 4 : INVENTAIRE ---
elif "4. Inventaire" in choix_etape:
    st.subheader("📋 Inventaire des pièces")
    branche = st.session_state.get('branche_active', "Droit général")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ✅ Pièces Reçues")
        if 'nom_fichier' in st.session_state:
            st.success(f"📄 {st.session_state['nom_fichier']}")
            
    with col2:
        st.markdown("#### ❌ Pièces Manquantes")
        with st.container(height=300): # Hauteur fixe pour la checklist
            if "Travail" in branche:
                docs = ["Contrat de travail", "Bulletins de salaire", "Lettre de licenciement", "Attestation employeur"]
            elif "Logement" in branche:
                docs = ["Bail", "Quittances", "État des lieux", "Dépôt de garantie"]
            else:
                docs = ["ID", "Justificatif", "Contrat"]
                
            for d in docs:
                st.checkbox(d, value=False)

# --- LES AUTRES ÉTAPES ---
else:
    st.info(f"🚧 Le module **{choix_etape}** est en attente de données ou de configuration.")
