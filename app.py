import streamlit as st
import pandas as pd
import os
from logic.router import qualifier_le_dossier
from logic.tools.reader import extraire_texte_pdf, extraire_dates_cles
from logic.tools.analyzer import analyser_validite_juridique

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

# 2. INITIALISATION DES DONNÉES
if not os.path.exists('data/dossier.csv'):
    if not os.path.exists('data'):
        os.makedirs('data')
    df = pd.DataFrame(columns=['id', 'nom', 'etape', 'branche', 'protocole', 'resume'])
    df.to_csv('data/dossier.csv', index=False)

# 3. BARRE LATÉRALE (NAVIGATION)
st.sidebar.title("⚖️ Fortas OS")
etapes = [
    "1. Qualification", "2. Chronologie", "3. Validité", "4. Inventaire",
    "5. Calculs", "6. Mise en demeure", "7. Riposte", "8. Saisine",
    "9. Mise en état", "10. Oralité", "11. Jugement", "12. Exécution"
]
choix_etape = st.sidebar.radio("Navigation du Protocole :", etapes)

# 4. LOGIQUE DES ÉTAPES (ZONE DE TRAVAIL)
st.title(f"📍 {choix_etape}")

# --- ÉTAPE 1 : QUALIFICATION ---
if "1. Qualification" in choix_etape:
    st.subheader("Analyse du dossier et orientation")
    col1, col2 = st.columns([2, 1])
    with col1:
        nom_client = st.text_input("Nom du dossier / Client :")
        faits = st.text_area("Exposez les faits de manière brute :", height=200)
        if st.button("Lancer l'Analyse"):
            if faits:
                resultat = qualifier_le_dossier(faits)
                st.success(f"Branche identifiée : {resultat['branche']}")
                st.info(resultat['message'])
                st.session_state['branche'] = resultat['branche']
                st.session_state['protocole'] = resultat['protocole']
            else:
                st.warning("Veuillez saisir les faits avant de lancer.")

# --- ÉTAPE 2 : CHRONOLOGIE ---
elif "2. Chronologie" in choix_etape:
    st.subheader("📅 Construction de la frise chronologique")
    st.write("Identifiez les moments clés pour vérifier les délais de prescription.")
    
    with st.expander("➕ Ajouter un événement marquant", expanded=True):
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            date_ev = st.date_input("Date de l'événement")
        with c2:
            desc_ev = st.text_input("Description", placeholder="Ex: Réception du courrier de licenciement")
        with c3:
            type_ev = st.selectbox("Source", ["Contrat", "Courrier", "Oral", "Fait matériel"])
        
        if st.button("Enregistrer l'événement"):
            st.toast(f"Événement du {date_ev} mémorisé !")
            
    st.divider()
    st.write("### 📂 Analyse de documents")
    
    fichier_uploade = st.file_uploader("Déposez un document (PDF) pour extraire les dates", type="pdf")
    
    if st.button("🔍 Lancer l'analyse automatique"):
        if fichier_uploade is not None:
            with st.spinner("Lecture du PDF..."):
                texte_extrait = extraire_texte_pdf(fichier_uploade)
                resultats_auto = extraire_dates_cles(texte_extrait)
                st.table(pd.DataFrame(resultats_auto))
                st.success("Analyse du document terminée !")
        else:
            st.warning("Veuillez d'abord déposer un fichier PDF.")

# --- ÉTAPE 3 : VALIDITÉ ---
elif "3. Validité" in choix_etape:
    st.subheader("⚖️ Audit de Validité Juridique")
    st.write("L'IA analyse la conformité des délais et des procédures.")
    
    if st.button("🧠 Lancer l'analyse de conformité"):
        with st.spinner("Analyse juridique en cours..."):
            # Ici on envoie un texte de test à l'IA
            resultat = analyser_validite_juridique("Analyse des délais et procédures du dossier Fortas")
            st.markdown("### 📋 Rapport d'Audit")
            st.info(resultat)

# --- LE RESTE ---
else:
    st.info(f"🚧 Le module **{choix_etape}** est en cours de configuration.")
