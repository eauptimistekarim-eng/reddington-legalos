import streamlit as st
import pandas as pd
import os
from logic.router import qualifier_le_dossier
from logic.tools.reader import extraire_texte_pdf, extraire_dates_cles
from logic.tools.analyzer import analyser_validite_juridique
from logic.tools.chatbot import reponse_chat_juridique

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
    </style>
    """, unsafe_allow_html=True)

# 2. INITIALISATION DES DONNÉES ET DOSSIERS
if not os.path.exists('data'):
    os.makedirs('data')

if not os.path.exists('data/dossier.csv'):
    df = pd.DataFrame(columns=['id', 'nom', 'etape', 'branche', 'protocole', 'resume'])
    df.to_csv('data/dossier.csv', index=False)

# 3. BARRE LATÉRALE (NAVIGATION)
st.sidebar.title("⚖️ Fortas OS")
etapes = ["1. Qualification", "2. Chronologie", "3. Validité", "4. Inventaire", "5. Calculs"]
choix_etape = st.sidebar.radio("Navigation :", etapes)

# 4. LOGIQUE DES ÉTAPES (ZONE DE TRAVAIL)
st.title(f"📍 {choix_etape}")

# --- ÉTAPE 1 : QUALIFICATION & CONVERSATION ---
if "1. Qualification" in choix_etape:
    col_gauche, col_droite = st.columns([1, 1], gap="large")

    with col_gauche:
        st.subheader("🧪 Analyse Poussée")
        faits = st.text_area("Exposez les faits bruts du dossier :", height=250)
        if st.button("Lancer le Diagnostic"):
            if faits:
                with st.spinner("Analyse technique..."):
                    res = qualifier_le_dossier(faits)
                    # On mémorise la branche pour les étapes suivantes
                    st.session_state['branche_active'] = res['branche']
                    st.success(f"Branche identifiée : {res['branche']}")
                    st.info(res['message'])
            else: 
                st.warning("Veuillez saisir des faits avant de lancer l'analyse.")

    with col_droite:
        st.subheader("💬 Assistant Consultant")
        # Initialisation de l'historique du chat s'il n'existe pas
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Container pour scroller le chat
        chat_container = st.container(height=400)
        with chat_container:
            for q, r in st.session_state.chat_history:
                with st.chat_message("user"):
                    st.write(q)
                with st.chat_message("assistant"):
                    st.write(r)

        # Entrée utilisateur
        prompt = st.chat_input("Posez une question sur le droit...")
        if prompt:
            with st.spinner("Réflexion..."):
                reponse = reponse_chat_juridique(prompt, st.session_state.chat_history)
                st.session_state.chat_history.append((prompt, reponse))
                st.rerun()

# --- ÉTAPE 2 : CHRONOLOGIE ---
elif "2. Chronologie" in choix_etape:
    st.subheader("📅 Chronologie & Lecture PDF")
    
    fichier_uploade = st.file_uploader("Déposez le document (PDF)", type="pdf")
    
    if st.button("🔍 Extraire les données"):
        if fichier_uploade:
            with st.spinner("L'IA lit le document..."):
                texte = extraire_texte_pdf(fichier_uploade)
                resultats = extraire_dates_cles(texte)
                
                # Sauvegarde pour l'étape 3
                st.session_state['donnees_du_pdf'] = resultats
                
                # Affichage propre en tableau
                if isinstance(resultats, list) and len(resultats) > 0:
                    df_final = pd.DataFrame(resultats)
                    st.table(df_final)
                else:
                    st.info("Aucune date précise n'a été extraite, mais le texte est mémorisé.")
                
                st.success("Analyse terminée ! Les données sont prêtes pour l'étape '3. Validité'.")
        else:
            st.warning("Veuillez déposer un fichier.")

# --- ÉTAPE 3 : VALIDITÉ ---
elif "3. Validité" in choix_etape:
    st.subheader("⚖️ Audit de Validité Juridique")
    
    # On vérifie si la mémoire contient des données PDF
    if 'donnees_du_pdf' in st.session_state:
        donnees = st.session_state['donnees_du_pdf']
        branche = st.session_state.get('branche_active', "Droit général")
        
        st.write(f"✅ **Document détecté.** Branche : **{branche}**")
        
        if st.button("🧠 Lancer l'analyse personnalisée"):
            with st.spinner("Analyse juridique en cours..."):
                # On envoie les données réelles et le contexte de branche à l'IA
                rapport = analyser_validite_juridique(str(donnees), contexte=branche)
                st.markdown(f"### 📋 Rapport d'Audit ({branche})")
                st.info(rapport)
    else:
        st.error("❌ Aucune donnée de document trouvée. Scannez un PDF à l'étape '2. Chronologie'.")

# --- LE RESTE ---
else:
    st.info(f"🚧 Le module **{choix_etape}** est en cours de configuration.")
