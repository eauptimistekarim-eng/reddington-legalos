import streamlit as st
from groq import Groq

st.set_page_config(page_title="Reddington LegalOS", layout="wide")

client = Groq(api_key="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")
MODEL_NAME = "llama-3.3-70b-versatile"

# Définition des prompts spécifiques par étape
METHODE = {
    "1. Faits": "Analyse les faits de manière brute. Identifie les contradictions et les points clés.",
    "2. Qualification": "Donne la qualification juridique exacte (Code Civil, Pénal, etc.) et les articles applicables.",
    "3. Preuves": "Liste les preuves nécessaires pour gagner. Qu'est-ce qui manque au dossier ?",
    "4. Intentions": "Analyse la psychologie de la partie adverse. Quel est leur but caché ?",
    "5. Procédure": "Quelle est la meilleure juridiction et la stratégie de timing (référé, fond, etc.) ?",
    "6. Avocat du Diable": "Prends la place du camp adverse et détruis nos arguments. Sois impitoyable.",
    "7. Riposte": "Propose une stratégie de contre-attaque inattendue pour renverser la table.",
    "8. Risques": "Évalue les probabilités d'échec et les conséquences financières/juridiques.",
    "9. Action": "Donne les 3 actions immédiates à faire dans les 24h.",
    "10. Rédaction": "Donne les éléments de langage précis à utiliser dans un courrier ou une assignation.",
    "11. Suivi": "Comment verrouiller le dossier sur le long terme ?"
}

st.title("🛡️ Reddington LegalOS - Stratégie Chirurgicale")
cas_juridique = st.text_area("Exposez les détails du dossier :", height=200)

if st.button("EXÉCUTER LA MÉTHODE COMPLÈTE"):
    if not cas_juridique:
        st.warning("Veuillez entrer les faits.")
    else:
        # Barre de progression pour suivre les 11 étapes
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        container = st.container()
        
        for i, (etape, instruction) in enumerate(METHODE.items()):
            status_text.text(f"Génération de : {etape}...")
            
            # Appel spécifique pour CHAQUE étape
            prompt = f"Tu es Raymond Reddington. {instruction} \n\nCAS : {cas_juridique}"
            
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                
                # Affichage progressif dans un "Expander" (volet déroulant)
                with container.expander(f"✅ {etape}", expanded=(i == 0)):
                    st.write(response.choices[0].message.content)
                
                # Mise à jour barre de progression
                progress_bar.progress((i + 1) / len(METHODE))
            
            except Exception as e:
                st.error(f"Erreur à l'étape {etape}: {e}")
        
        status_text.text("👑 Stratégie Reddington terminée avec succès.")
