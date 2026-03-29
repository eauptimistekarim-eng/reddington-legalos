import streamlit as st
import pandas as pd
import os
from logic.router import qualifier_le_dossier

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="Fortas OS - Intelligence Juridique", 
    layout="wide", 
    page_icon="⚖️"
)

# 2. DESIGN PERSONNALISÉ (CSS)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3em; 
        background-color: #1E3A8A; 
        color: white;
        font-weight: bold;
    }
    .stTextArea>div>div>textarea { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. INITIALISATION DES DONNÉES (Le Dossier CSV)
if not os.path.exists('data/dossier.csv'):
    # Création de la structure de base si absente
    df = pd.DataFrame(columns=['id', 'nom', 'etape', 'branche', 'protocole', 'resume'])
    df.to_csv('data/dossier.csv', index=False)

# 4. BARRE LATÉRALE ( NAVIGATION ET PROTOCOLE )
st.sidebar.image("https://img.icons8.com/fluency/96/law.png", width=60)
st.sidebar.title("Fortas OS")
st.sidebar.caption("Système d'Ingénierie Juridique")
st.sidebar.write("---")

etapes = [
    "1. Qualification", "2. Chronologie", "3. Validité", "4. Inventaire",
    "5. Calculs", "6. Mise en demeure", "7. Riposte", "8. Saisine",
    "9. Mise en état", "10. Oralité", "11. Jugement", "12. Exécution"
]

# Navigation entre les 12 étapes
choix_etape = st.sidebar.radio("Suivi du Protocole :", etapes)

st.sidebar.write("---")
st.sidebar.info("💡 **Statut :** Connecté au moteur logic/router.py")

# 5. ZONE DE TRAVAIL PRINCIPALE
st.title(f"📍 {choix_etape}")

# --- ÉTAPE 1 : QUALIFICATION ---
if "1. Qualification" in choix_etape:
    st.subheader("Analyse du dossier et orientation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        nom_client = st.text_input("Nom du dossier ou du client :", placeholder="Ex: Dossier Dupont / Licenciement")
        faits = st.text_area(
            "Exposez les faits de manière brute :", 
            height=250, 
            placeholder="Décrivez ici la situation (ex: dates, messages reçus, actions du patron...)"
        )
        
        if st.button("Lancer l'Analyse"):
            if faits:
                # APPEL AU CERVEAU DANS LOGIC/ROUTER.PY
                resultat = qualifier_le_dossier(faits)
                
                st.divider()
                st.success(f"⚖️ **Branche identifiée :** {resultat['branche']}")
                st.info(f"🚀 **Protocole activé :** {resultat['protocole']}")
                st.write(resultat['message'])
                
                # Sauvegarde temporaire dans la session
                st.session_state['branche'] = resultat['branche']
                st.session_state['protocole'] = resultat['protocole']
            else:
                st.warning("⚠️ Veuillez saisir les faits avant de lancer l'analyse.")

    with col2:
        st.write("### 📜 Aide à la saisie")
        st.caption("""
        Pour une qualification précise, essayez d'inclure :
        - Le lien (Employeur, Propriétaire, Voisin)
        - L'action principale (Licenciement, Loyer impayé, Nuisance)
        - L'objectif (Récupérer de l'argent, Annuler un contrat)
        """)
        
        if 'branche' in st.session_state:
            st.metric("Branche actuelle", st.session_state['branche'])

# --- ÉTAPES SUIVANTES (À CODER) ---
else:
    st.warning(f"Le module pour '{choix_etape}' est en cours de configuration.")
    st.info("Cette étape sera connectée aux fichiers dans logic/core/ et logic/tools/.")
