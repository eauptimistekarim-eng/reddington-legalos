import streamlit as st
from logic.router import qualifier_le_dossier
from logic.processor import classifier_procedure_universelle

def afficher_qualification():
    # Initialisation des variables de session
    if "analyse_complete" not in st.session_state: st.session_state.analyse_complete = ""
    if "branche_active" not in st.session_state: st.session_state.branche_active = "Non définie"
    if "cat_procedure" not in st.session_state: st.session_state.cat_procedure = "Non définie"
    if "acte_detecte" not in st.session_state: st.session_state.acte_detecte = "Non détecté"

    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    
    # Zone de saisie des faits
    faits = st.text_area("Exposition des faits (Détaillez la situation) :", height=200, placeholder="Ex: Je suis salarié depuis 2005...")
    
    if st.button("🚀 LANCER L'ANALYSE REDDINGTON"):
        if faits:
            with st.spinner("Qualification juridique en cours..."):
                # 1. Appel à l'IA pour le rapport de fond
                res = qualifier_le_dossier(faits)
                
                # 2. Appel au processeur de règles pour les badges (Branche, Cat, Acte)
                # On récupère bien les 3 valeurs ici pour éviter l'erreur ValueError
                branche, cat, acte = classifier_procedure_universelle(res['message'], faits)
                
                # Mise à jour de la session
                st.session_state.analyse_complete = res['message']
                st.session_state.branche_active = branche
                st.session_state.cat_procedure = cat
                st.session_state.acte_detecte = acte
                st.rerun()

    # Affichage des résultats
    if st.session_state.analyse_complete:
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Branche :**\n{st.session_state.branche_active}")
        with col2:
            st.warning(f"**Procédure :**\n{st.session_state.cat_procedure}")
        with col3:
            st.success(f"**Acte suggéré :**\n{st.session_state.acte_detecte}")

        st.markdown("### 📋 Rapport de Qualification & Stratégie")
        st.write(st.session_state.analyse_complete)
    
    st.markdown('</div>', unsafe_allow_html=True)
