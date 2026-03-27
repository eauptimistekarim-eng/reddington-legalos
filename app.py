import streamlit as st
from groq import Groq

# 1. Config
st.set_page_config(page_title="Reddington LegalOS", layout="wide", page_icon="🛡️")

# 2. Initialisation
client = Groq(api_key="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")
MODEL_NAME = "llama-3.3-70b-versatile"

# 3. Dictionnaire par défaut des instructions (Personnalisable dans l'interface)
DEFAULT_METHODE = {
    "📌 1. Faits": "Analyse les faits de manière brute. Identifie les contradictions.",
    "⚖️ 2. Qualification": "Donne la qualification juridique exacte et les articles applicables.",
    "🔎 3. Preuves": "Liste les preuves nécessaires. Qu'est-ce qui manque ?",
    "🧠 4. Intentions": "Analyse la psychologie adverse. Quel est leur but caché ?",
    "🏛️ 5. Procédure": "Meilleure juridiction et stratégie de timing ?",
    "👹 6. Avocat du Diable": "Détruis nos arguments de manière impitoyable.",
    "💥 7. Riposte": "Stratégie de contre-attaque inattendue.",
    "⚠️ 8. Risques": "Évalue les probabilités d'échec.",
    "📅 9. Action": "Donne les 3 actions immédiates (24h).",
    "📝 10. Rédaction": "Éléments de langage pour courriers ou assignations.",
    "🔒 11. Suivi": "Comment verrouiller le dossier sur le long terme ?"
}

st.title("🛡️ Reddington LegalOS - Custom Edition")

# --- SIDEBAR DE PERSONNALISATION ---
st.sidebar.title("⚙️ Personnaliser la Méthode")
st.sidebar.info("Modifiez les instructions ci-dessous pour ajuster l'analyse.")

custom_prompts = {}
selected_steps = []

for etape, desc in DEFAULT_METHODE.items():
    # Case à cocher pour activer l'étape
    activated = st.sidebar.checkbox(f"Activer {etape.split('.')[0]}", value=True)
    # Zone de texte pour modifier l'instruction du prompt
    instruction = st.sidebar.text_area(f"Instruction pour {etape.split('.')[0]}", value=desc, height=80)
    
    if activated:
        selected_steps.append(etape)
        custom_prompts[etape] = instruction

# --- ZONE PRINCIPALE ---
cas_juridique = st.text_area("Exposez les détails du dossier :", height=200)

if st.button("LANCER L'ANALYSE PERSONNALISÉE"):
    if not cas_juridique:
        st.warning("⚠️ Veuillez entrer les détails du dossier.")
    elif not selected_steps:
        st.error("❌ Veuillez sélectionner au moins une étape dans la barre latérale.")
    else:
        progress_bar = st.progress(0)
        status = st.empty()
        
        for i, etape in enumerate(selected_steps):
            status.text(f"Génération : {etape}...")
            
            prompt = f"""
            Tu es Raymond Reddington. {custom_prompts[etape]}
            Détails du cas : {cas_juridique}
            Réponds de manière stratégique et précise.
            """
            
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                with st.expander(etape, expanded=True):
                    st.markdown(response.choices[0].message.content)
                progress_bar.progress((i + 1) / len(selected_steps))
            except Exception as e:
                st.error(f"Erreur sur {etape}: {e}")
        
        status.success("✅ Analyse terminée.")
        st.balloons()
