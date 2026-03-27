import streamlit as st
from groq import Groq

# 1. Configuration
st.set_page_config(page_title="Reddington LegalOS", layout="wide")

# 2. Moteur (Llama 3.3)
client = Groq(api_key="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")
MODEL_NAME = "llama-3.3-70b-versatile"

# 3. Interface
st.title("🛡️ Reddington LegalOS")
st.markdown("### *Intelligence Artificielle de Stratégie Juridique*")

cas = st.text_area("Exposez les faits ici :", height=200)

if st.button("LANCER L'ANALYSE"):
    if not cas:
        st.warning("Veuillez entrer du texte.")
    else:
        with st.spinner("Reddington analyse..."):
            try:
                # Appels API
                res_red = client.chat.completions.create(
                    model=MODEL_NAME, 
                    messages=[{"role": "user", "content": f"Tu es Reddington. Analyse stratégique : {cas}"}]
                )
                res_dev = client.chat.completions.create(
                    model=MODEL_NAME, 
                    messages=[{"role": "user", "content": f"Tu es l'Avocat du Diable. Trouve les failles : {cas}"}]
                )

                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("📜 Stratégie Reddington")
                    st.info(res_red.choices[0].message.content)
                with c2:
                    st.subheader("👹 L'Avocat du Diable")
                    st.error(res_dev.choices[0].message.content)
            except Exception as e:
                st.error(f"Erreur : {e}")
