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
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        background-color: #1E3A8A; 
        color: white; 
        font-weight: bold;
        height: 3em;
    }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. INITIALISATION DE LA MÉMOIRE
if "messages" not in st.session_state:
    st.session_state.messages = []
if "branche_active" not in st.session_state:
    st.session_state.branche_active = "Droit général"
if not os.path.exists('data'):
    os.makedirs('data')

# 3. BARRE LATÉRALE (NAVIGATION)
st.sidebar.title("⚖️ Fortas OS")
etapes = ["1. Qualification", "2. Chronologie", "3. Validité", "4. Inventaire", "5. Calculs"]
choix_etape = st.sidebar.radio("Navigation du Protocole :", etapes)

# 4. LOGIQUE DES ÉTAPES
st.title(f"📍 {choix_etape}")

# --- ÉTAPE 1 : QUALIFICATION & CONVERSATION ---
if "1. Qualification" in choix_etape:
    col_g, col_d = st.columns([1, 1], gap="large")

    with col_g:
        st.subheader("🧪 Analyse Poussée")
        faits = st.text_area("Exposez les faits bruts du dossier :", height=300, key="faits_zone")
        if st.button("Lancer le Diagnostic"):
            if faits:
                with st.spinner("Analyse technique..."):
                    res = qualifier_le_dossier(faits)
                    st.session_state['branche_active'] = res['branche']
                    st.success(f"Branche identifiée : {res['branche']}")
                    st.info(res['message'])
            else:
                st.warning("Veuillez saisir des faits.")

    with col_d:
        st.subheader("💬 Assistant Consultant")
        
        # Affichage de l'historique existant
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Zone d'entrée du chat avec effet de streaming
        if prompt := st.chat_input("Posez une question juridique..."):
            # Ajouter et afficher le message utilisateur
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Générer et afficher la réponse progressivement
            with st.chat_message("assistant"):
                hist = [(m["content"], "") for m in st.session_state.messages if m["role"] == "user"]
                # Utilisation du générateur pour l'effet mot à mot
                reponse_complete = st.write_stream(reponse_chat_juridique_stream(prompt, hist))
            
            # Sauvegarder la réponse complète dans l'historique
            st.session_state.messages.append({"role": "assistant", "content": reponse_complete})

# --- ÉTAPE 2 : CHRONOLOGIE ---
elif "2. Chronologie" in choix_etape:
    st.subheader("📅 Chronologie & Lecture PDF")
    fichier = st.file_uploader("Déposez le document (PDF)", type="pdf")
    
    if st.button("🔍 Extraire les données"):
        if fichier:
            with st.spinner("Extraction en cours..."):
                texte = extraire_texte_pdf(fichier)
                resultats = extraire_dates_cles(texte)
                st.session_state['donnees_du_pdf'] = resultats
                st.session_state['nom_fichier'] = fichier.name
                
                if isinstance(resultats, list) and len(resultats) > 0:
                    st.table(pd.DataFrame(resultats))
                else:
                    st.info("Document lu, mais aucune date standard détectée.")
                st.success("Analyse terminée ! Les données sont prêtes pour l'étape 3.")
        else:
            st.warning("Veuillez charger un fichier.")

# --- ÉTAPE 3 : VALIDITÉ ---
elif "3. Validité" in choix_etape:
    st.subheader("⚖️ Audit de Validité")
    if 'donnees_du_pdf' in st.session_state:
        donnees = st.session_state['donnees_du_pdf']
        branche = st.session_state['branche_active']
        st.write(f"✅ Analyse basée sur le document : **{st.session_state.get('nom_fichier')}**")
        
        if st.button("🧠 Lancer l'analyse de conformité"):
            with st.spinner("L'IA examine les délais..."):
                rapport = analyser_validite_juridique(str(donnees), contexte=branche)
                st.markdown("### 📋 Rapport d'Audit")
                st.info(rapport)
    else:
        st.error("⚠️ Aucun document scanné. Allez d'abord à l'étape '2. Chronologie'.")

# --- ÉTAPE 4 : INVENTAIRE ---
elif "4. Inventaire" in choix_etape:
    st.subheader("📋 Inventaire des pièces")
    branche = st.session_state.get('branche_active', "Droit général")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ✅ Pièces Reçues")
        if 'nom_fichier' in st.session_state:
            st.success(f"📄 {st.session_state['nom_fichier']}")
        else:
            st.write("Aucun document scanné pour le moment.")
            
    with col2:
        st.markdown("#### ❌ Pièces Manquantes")
        if "Travail" in branche:
            docs = ["Contrat de travail", "Bulletins de salaire", "Lettre de licenciement"]
        elif "Logement" in branche:
            docs = ["Bail", "Quittances", "État des lieux"]
        else:
            docs = ["Pièce d'identité", "Justificatifs", "Contrats"]
            
        for d in docs:
            st.checkbox(d, value=False)

# --- LE RESTE ---
else:
    st.info(f"🚧 Le module **{choix_etape}** sera bientôt disponible.")
