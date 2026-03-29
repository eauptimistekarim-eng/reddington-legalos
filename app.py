import streamlit as st
import pandas as pd
import os
from logic.router import qualifier_le_dossier
from logic.tools.reader import extraire_texte_pdf, extraire_dates_cles
from logic.tools.analyzer import analyser_validite_juridique
from logic.tools.chatbot import reponse_chat_juridique

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
                    st.session_state['branche_active'] = res['branche']
                    st.success(f"Branche : {res['branche']}")
                    st.info(res['message'])
            else: st.warning("Veuillez saisir des faits.")

    with col_droite:
        st.subheader("💬 Assistant Consultant")
        # Initialisation de l'historique du chat
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Zone d'affichage du chat
        for q, r in st.session_state.chat_history:
            with st.chat_message("user"): st.write(q)
            with st.chat_message("assistant"): st.write(r)

        # Entrée utilisateur
        prompt = st.chat_input("Posez une question sur le droit...")
        if prompt:
            reponse = reponse_chat_juridique(prompt, st.session_state.chat_history)
            st.session_state.chat_history.append((prompt, reponse))
            st.rerun() # Pour rafraîchir l'affichage du chat
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
    
    fichier_uploade = st.file_uploader("Déposez le document (PDF)", type="pdf")
    
    if st.button("🔍 Extraire les données"):
        if fichier_uploade:
            with st.spinner("Lecture en cours..."):
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
                
                st.success("Analyse terminée ! Vous pouvez consulter l'onglet '3. Validité'.")
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
