import streamlit as st
import pandas as pd
import os
from logic.router import qualifier_le_dossier
from logic.tools.reader import extraire_texte_pdf, extraire_dates_cles
from logic.tools.analyzer import analyser_validite_juridique
from logic.tools.chatbot import reponse_chat_juridique_stream

# 1. CONFIGURATION ET STYLE DASHBOARD
st.set_page_config(page_title="Fortas OS", layout="wide", page_icon="⚖️")

st.markdown("""
    <style>
    /* Fond de page gris clair pro */
    .main { background-color: #f4f7f9; }
    
    /* Tuiles (Cards) Blanches */
    .css-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e0e6ed;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Boîtes de contenu avec scroll interne fixe */
    .scroll-box {
        height: 450px;
        overflow-y: auto;
        padding: 15px;
        border-radius: 8px;
        background-color: #ffffff;
        border: 1px solid #f0f2f6;
        line-height: 1.6;
    }
    
    /* Bouton avec dégradé */
    .stButton>button {
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        border: none;
        font-weight: 600;
        border-radius: 8px;
        height: 3.5em;
        transition: 0.3s;
    }
    .stButton>button:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 4px 12px rgba(30,58,138,0.3); 
    }

    /* Titres de sections */
    .section-title {
        color: #1E3A8A;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INITIALISATION DE LA MÉMOIRE (Session State)
if "messages" not in st.session_state: st.session_state.messages = []
if "analyse_gpt" not in st.session_state: st.session_state.analyse_gpt = ""
if "conseils_automatiques" not in st.session_state: st.session_state.conseils_automatiques = ""
if "branche_active" not in st.session_state: st.session_state.branche_active = "Non définie"

# 3. BARRE LATÉRALE (Navigation)
st.sidebar.title("⚖️ Fortas OS")
etapes = ["1. Qualification", "2. Chronologie", "3. Validité", "4. Inventaire", "5. Calculs"]
choix_etape = st.sidebar.radio("Protocole de traitement :", etapes)

# 4. ÉTAPE 1 : LE DASHBOARD STRATÉGIQUE
if "1. Qualification" in choix_etape:
    st.markdown(f"## 📍 {choix_etape}")
    
    # --- ZONE DE SAISIE (Pleine Largeur) ---
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📝 Exposition des Faits & Prétentions</div>', unsafe_allow_html=True)
    faits = st.text_area("", height=180, placeholder="Saisissez ici les faits bruts du dossier pour lancer l'intelligence artificielle...", label_visibility="collapsed")
    
    if st.button("🚀 ANALYSER LE DOSSIER & GÉNÉRER LA PROCÉDURE"):
        if faits:
            with st.spinner("Analyse stratégique en cours..."):
                # 1. Appel au Router pour l'analyse stratégique
                res = qualifier_le_dossier(faits)
                st.session_state.analyse_gpt = res['message']
                st.session_state.branche_active = res['branche']
                
                # 2. Extraction automatique de la fiche procédure
                with st.spinner("Rédaction de la fiche de procédure..."):
                    prompt_proc = f"""
                    Basé sur cette analyse : {res['message']}
                    Donne-moi une fiche pratique contenant :
                    1. Les articles de loi et visas applicables.
                    2. Les délais de prescription ou de procédure.
                    3. La liste des étapes à suivre.
                    Réponds de manière structurée.
                    """
                    gen = reponse_chat_juridique_stream(prompt_proc, [])
                    st.session_state.conseils_automatiques = "".join(list(gen))
                st.rerun()
        else:
            st.warning("Veuillez saisir des faits avant de lancer l'analyse.")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- ZONE DE RÉSULTATS (Deux Colonnes) ---
    col_strat, col_proc = st.columns(2, gap="medium")

    with col_strat:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">🧠 Stratégie : {st.session_state.branche_active}</div>', unsafe_allow_html=True)
        # Scroll-box pour l'analyse GPT
        st.markdown(f'''
            <div class="scroll-box">
                {st.session_state.analyse_gpt if st.session_state.analyse_gpt else "<i>L'analyse stratégique apparaîtra ici après avoir cliqué sur le bouton.</i>"}
            </div>
        ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_proc:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📚 Fiche Procédure & Articles</div>', unsafe_allow_html=True)
        # Scroll-box pour la fiche de procédure
        st.markdown(f'''
            <div class="scroll-box">
                {st.session_state.conseils_automatiques if st.session_state.conseils_automatiques else "<i>Les articles de loi et conseils pratiques s'afficheront ici.</i>"}
            </div>
        ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- CHAT COLLABORATIF (Optionnel) ---
    if st.session_state.analyse_gpt:
        with st.expander("💬 Approfondir avec le Collaborateur Juridique"):
            chat_box = st.container(height=350)
            if prompt := st.chat_input("Ex: Peux-tu me rédiger une clause de non-concurrence adaptée ?"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with chat_box:
                    for m in st.session_state.messages: 
                        with st.chat_message(m["role"]): st.markdown(m["content"])
                    with st.chat_message("assistant"):
                        ctx = f"Analyse : {st.session_state.analyse_gpt}. Conseils : {st.session_state.conseils_automatiques}"
                        reponse = st.write_stream(reponse_chat_juridique_stream(f"Contexte: {ctx}\nQuestion: {prompt}", []))
                st.session_state.messages.append({"role": "assistant", "content": reponse})

# --- AUTRES ÉTAPES ---
elif "2. Chronologie" in choix_etape:
    st.markdown(f"## 📍 {choix_etape}")
    st.subheader("📅 Lecture et extraction chronologique")
    fichier = st.file_uploader("Charger le dossier client (PDF)", type="pdf")
    if fichier and st.button("Extraire les dates"):
        with st.spinner("Lecture du document..."):
            texte = extraire_texte_pdf(fichier)
            resultats = extraire_dates_cles(texte)
            st.table(pd.DataFrame(resultats))

elif "4. Inventaire" in choix_etape:
    st.markdown(f"## 📍 {choix_etape}")
    st.subheader("📋 Liste des pièces indispensables")
    st.write(f"Branche détectée : **{st.session_state.branche_active}**")
    st.checkbox("Mandat de représentation")
    st.checkbox("Contrat de base")
    st.checkbox("Preuves des faits (Emails, courriers)")

else:
    st.markdown(f"## 📍 {choix_etape}")
    st.info(f"Le module **{choix_etape}** est prêt à recevoir vos données.")
