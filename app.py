import streamlit as st
from groq import Groq

# 1. Configuration de la page
st.set_page_config(page_title="Reddington LegalOS", layout="wide", page_icon="🛡️")

# 2. Initialisation
client = Groq(api_key="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")
MODEL_NAME = "llama-3.3-70b-versatile"

# 3. Définition de la Méthode Reddington
METHODE = {
    "📌 1. Analyse des Faits": "Analyse les faits de manière brute. Identifie les contradictions et les points clés.",
    "⚖️ 2. Qualification Juridique": "Donne la qualification juridique exacte (Code Civil, Pénal, etc.) et les articles applicables.",
    "🔎 3. Inventaire des Preuves": "Liste les preuves nécessaires pour gagner. Qu'est-ce qui manque au dossier ?",
    "🧠 4. Analyse des Intentions": "Analyse la psychologie de la partie adverse. Quel est leur but caché ?",
    "🏛️ 5. Stratégie de Procédure": "Quelle est la meilleure juridiction et la stratégie de timing (référé, fond, etc.) ?",
    "👹 6. L'Avocat du Diable": "Prends la place du camp adverse et détruis nos arguments. Sois impitoyable.",
    "💥 7. Riposte (Contre-Attaque)": "Propose une stratégie de contre-attaque inattendue pour renverser la table.",
    "⚠️ 8. Évaluation des Risques": "Évalue les probabilités d'échec et les conséquences financières/juridiques.",
    "📅 9. Plan d'Action (24h)": "Donne les 3 actions immédiates à faire dans les 24h.",
    "📝 10. Éléments de Rédaction": "Donne les éléments de langage précis à utiliser dans un courrier ou une assignation.",
    "🔒 11. Protocole de Suivi": "Comment verrouiller le dossier sur le long terme ?"
}

# 4. Interface Utilisateur
st.title("🛡️ Reddington LegalOS")
st.markdown("#### *Intelligence Artificielle de Haute Stratégie Juridique*")
st.divider()

cas_juridique = st.text_area("Exposez les détails de votre dossier :", height=200, placeholder="Entrez les faits ici...")

if st.button("EXÉCUTER L'ANALYSE CHIRURGICALE"):
    if not cas_juridique:
        st.warning("⚠️ Veuillez entrer les détails du dossier.")
    else:
        # Création de l'espace de résultat
        progress_bar = st.progress(0)
        status = st.empty()
        
        # On lance les 11 étapes
        for i, (etape, instruction) in enumerate(METHODE.items()):
            status.text(f"Génération : {etape}...")
            
            prompt = f"""
            Tu es Raymond Reddington, consultant en gestion de risques juridiques.
            {instruction}
            
            Détails du cas : {cas_juridique}
            
            Réponds avec autorité, précision et un ton stratégique.
            """
            
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                
                with st.expander(etape, expanded=(i == 0)):
                    st.markdown(response.choices[0].message.content)
                
                progress_bar.progress((i + 1) / len(METHODE))
            
            except Exception as e:
                st.error(f"Erreur sur {etape}: {e}")
        
        status.success("✅ Analyse Reddington terminée.")
        st.balloons()

st.sidebar.markdown("---")
st.sidebar.info("Méthode Reddington v2.0 - Propulsé par Llama 3.3 70B")
