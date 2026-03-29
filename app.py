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
    if not os.path.exists('data'): os.makedirs('data')
    df = pd.DataFrame(columns=['id', 'nom', 'etape', 'branche', 'protocole', 'resume'])
    df.to_csv('data/dossier.csv', index=False)

# 3. BARRE LATÉRALE (NAVIGATION)
st.sidebar.title("⚖️ Fortas OS")
etapes = ["1. Qualification", "2. Chronologie", "3. Validité", "4. Inventaire", "5. Calculs"]
choix_etape = st.sidebar.radio("Navigation :", etapes)

# 4. LOGIQUE DES ÉTAPES
st.title(f"📍 {choix_etape}")

# --- ÉTAPE 1 : QUALIFICATION ---
if "1. Qualification" in choix_etape:
    st.subheader("Analyse du dossier")
    faits = st.text_area("Exposez les faits :", height=200)
    if st.button("Lancer l'Analyse"):
        if faits:
            resultat = qualifier_le_dossier(faits)
            st.success(f"Branche : {resultat['branche']}")
            st.info(resultat['message'])
        else:
            st.warning("Saisissez les faits.")

# --- ÉTAPE 2 : CHRONOLOGIE ---
elif "2. Chronologie" in choix_etape:
    st.subheader("📅 Chronologie & Lecture PDF")
    
    fichier_uploade = st.file_uploader("Déposez le document Pôle Emploi / IAE (PDF)", type="pdf")
    
    if st.button("🔍 Extraire les données du document"):
        if fichier_uploade:
            with st.spinner("L'IA lit le document..."):
                texte = extraire_texte_pdf(fichier_uploade)
                resultats = extraire_dates_cles(texte)
                
                # CRUCIAL : On stocke dans la mémoire de la session
                st.session_state['donnees_du_pdf'] = resultats
                
                st.table(pd.DataFrame(resultats))
                st.success("Données mémorisées ! Passez à l'étape 3.")
        else:
            st.warning("Veuillez déposer un fichier.")

# --- ÉTAPE 3 : VALIDITÉ ---
elif "3. Validité" in choix_etape:
    st.subheader("⚖️ Audit de Validité Juridique")
    
    # On vérifie si la mémoire contient quelque chose
    if 'donnees_du_pdf' in st.session_state:
        donnees = st.session_state['donnees_du_pdf']
        st.write("✅ **Document détecté.** Prêt pour l'audit de conformité.")
        
        if st.button("🧠 Lancer l'analyse personnalisée"):
            with st.spinner("Analyse en cours..."):
                # On envoie les vraies données (Pôle Emploi, etc.) à l'IA
                rapport = analyser_validite_juridique(str(donnees))
                st.markdown("### 📋 Rapport d'Audit (Basé sur votre document)")
                st.info(rapport)
    else:
        st.error("❌ Aucune donnée trouvée. Retournez à l'étape 2 pour scanner le document.")

# --- LE RESTE ---
else:
    st.info(f"🚧 Le module {choix_etape} est en cours.")
