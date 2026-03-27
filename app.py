import streamlit as st
from groq import Groq

# 1. Configuration de l'interface
st.set_page_config(page_title="Fortas LegalOS", layout="wide", page_icon="⚖️")

# 2. Initialisation Groq
client = Groq(api_key="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")
MODEL_NAME = "llama-3.3-70b-versatile"

# 3. La Méthode Fortas (Configurable)
DEFAULT_METHODE = {
    "📌 1. Analyse des Faits": "Analyse les faits de manière brute. Identifie les contradictions et les non-dits.",
    "⚖️ 2. Qualification Juridique": "Donne la qualification juridique exacte et les articles de loi applicables.",
    "🔎 3. Inventaire des Preuves": "Liste les preuves nécessaires pour gagner. Qu'est-ce qui manque au dossier ?",
    "🧠 4. Analyse des Intentions": "Analyse la psychologie de la partie adverse. Quel est leur but caché ?",
    "🏛️ 5. Stratégie de Procédure": "Quelle est la meilleure juridiction et le timing idéal (référé, fond) ?",
    "👹 6. L'Avocat du Diable": "Prends la place du camp adverse et détruis nos arguments de manière impitoyable.",
    "💥 7. Riposte Stratégique": "Propose une stratégie de contre-attaque inattendue pour renverser la situation.",
    "⚠️ 8. Évaluation des Risques": "Évalue froidement les probabilités d'échec et les conséquences possibles.",
    "📅 9. Plan d'Action (24h)": "Donne les 3 actions immédiates à réaliser dans les prochaines 24 heures.",
    "📝 10. Éléments de Rédaction": "Donne les éléments de langage précis pour un courrier ou une assignation.",
    "🔒 11. Protocole de Suivi": "Comment verrouiller le dossier pour garantir un succès sur le long terme ?"
}

# --- INTERFACE ---
st.title("⚖️ Fortas LegalOS")
st.markdown("##### *Système Expert de Haute Stratégie Juridique*")
st.divider()

# --- SIDEBAR DE PERSONNALISATION ---
st.sidebar.title("⚙️ Configuration Fortas")
st.sidebar.write("Personnalisez les prompts de chaque étape :")

custom_prompts = {}
selected_steps = []

for etape, desc in DEFAULT_METHODE.items():
    # Case à cocher pour activer/désactiver l'étape
    activated = st.sidebar.checkbox(f"Activer {etape.split('.')[0]}", value=True)
    # Zone de texte pour modifier l'instruction en temps réel
    instruction = st.sidebar.text_area(f"Instruction pour {etape.split('.')[1]}", value=desc, height=70)
    
    if activated:
        selected_steps.append(etape)
        custom_prompts[etape] = instruction

# --- ZONE DE TRAVAIL ---
cas_juridique = st.text_area("Détaillez les éléments du dossier :", height=200, placeholder="Exposez les faits ici...")

if st.button("LANCER L'ANALYSE FORTAS"):
    if not cas_juridique:
        st.warning("⚠️ Veuillez entrer les détails du cas avant de lancer Fortas.")
    elif not selected_steps:
        st.error("❌ Veuillez sélectionner au moins une étape dans la barre latérale.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, etape in enumerate(selected_steps):
            status_text.text(f"Exécution de l'étape : {etape}...")
            
            # L'IA sait qu'elle est l'expert Fortas
            full_prompt = f"""
            Tu es l'expert stratégique Fortas. Ta mission est d'exécuter cette instruction : {custom_prompts[etape]}
            
            Dossier à traiter : {cas_juridique}
            
            Réponds avec une précision chirurgicale, un ton froid et une vision de haute stratégie.
            """
            
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": full_prompt}],
                    temperature=0.2
                )
                with st.expander(etape, expanded=True):
                    st.markdown(response.choices[0].message.content)
                
                progress_bar.progress((i + 1) / len(selected_steps))
            except Exception as e:
                st.error(f"Erreur sur {etape}: {e}")
        
        status_text.success("✅ Analyse Fortas terminée.")
        st.balloons()

st.sidebar.divider()
st.sidebar.caption("Fortas LegalOS v2.2")
