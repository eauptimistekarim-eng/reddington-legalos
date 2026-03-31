import streamlit as st
import time
from processor import extract_text_from_pdf, get_freeman_prompt

# ... (Garder tes styles CSS et l'init du client Groq) ...

def typewriter_effect(text):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(f'<div class="kareem-box">{full_text}▌</div>', unsafe_allow_html=True)
        time.sleep(0.005) # Très rapide pour ne pas frustrer l'utilisateur
    container.markdown(f'<div class="kareem-box">{full_text}</div>', unsafe_allow_html=True)

# DANS TON DASHBOARD PRINCIPAL
with col_left:
    st.markdown(f"### 🖋️ ÉTAPE {st.session_state.step + 1} : {STEPS[st.session_state.step]}")
    
    # 📂 NOUVEAU : UPLOAD PDF
    uploaded_file = st.file_uploader("Transférer un document PDF (conclusions, contrat...)", type="pdf")
    if uploaded_file:
        pdf_content = extract_text_from_pdf(uploaded_file)
        st.session_state.data[st.session_state.step] = pdf_content[:4000] # On prend les 4000 premiers caractères
        st.success("PDF analysé par Kareem !")

    input_text = st.text_area("Données du dossier :", value=st.session_state.data[st.session_state.step], height=300)
    
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("🚀 ANALYSE KAREEM"):
            if len(input_text) > 10:
                with st.spinner("Kareem réfléchit..."):
                    # On appelle le prompt Freeman
                    p = get_freeman_prompt(STEPS[st.session_state.step], input_text)
                    resp = client.chat.completions.create(
                        messages=[{"role": "user", "content": p}],
                        model="llama-3.3-70b-versatile",
                    )
                    report = resp.choices[0].message.content
                    st.session_state.ai_reports[st.session_state.step] = report
                    typewriter_effect(report) # L'effet visuel
            else:
                st.warning("Précisez les faits pour Kareem.")
