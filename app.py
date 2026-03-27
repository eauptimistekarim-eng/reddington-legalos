import streamlit as st
from groq import Groq

st.set_page_config(page_title="Reddington LegalOS", layout="wide")

client = Groq(api_key="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")
MODEL_NAME = "llama-3.3-70b-versatile"

st.title("🛡️ Reddington LegalOS - Full Méthode")
cas_juridique = st.text_area("Exposez les détails du dossier :", height=200)

if st.button("LANCER L'ANALYSE MÉTHODIQUE"):
    if not cas_juridique:
        st.warning("Veuillez entrer les faits.")
    else:
        with st.spinner("Exécution des 11 étapes Reddington..."):
            try:
                # Le Super Prompt avec les 11 étapes détaillées
                prompt_red = f"""
                Tu es Raymond Reddington. Analyse ce cas en 11 étapes distinctes. 
                Sois cynique, brillant et chirurgical.
                1. Faits, 2. Qualification, 3. Preuves, 4. Intentions, 5. Procédure, 
                6. Avocat du Diable, 7. Riposte, 8. Risques, 9. Action, 10. Rédaction, 11. Suivi.
                CAS : {cas_juridique}
                """
                
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt_red}],
                    temperature=0.2
                )
                
                st.subheader("📜 Rapport Stratégique Complet")
                # Affichage propre
                st.markdown(response.choices[0].message.content)

            except Exception as e:
                st.error(f"Erreur : {e}")
