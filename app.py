"""
Viral Strategist Pro - Análise de Vídeos com Google Gemini
Versão com API Key Fixada no Código
"""

import streamlit as st
import google.generativeai as genai
import os
import tempfile

# ============================================
# 🔑 COLE SUA API KEY ABAIXO
# ============================================
GEMINI_API_KEY = "AIzaSyD8ijELhs2zJKFksT6w6qidZ21aLGGdcC0"
# ============================================

st.set_page_config(
    page_title="Viral Strategist Pro",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="expanded"
)

def configure_gemini(api_key):
    genai.configure(api_key=api_key)

def save_uploaded_file(uploaded_file):
    try:
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"Erro ao salvar arquivo: {e}")
        return None

def analyze_video_with_gemini(file_path, api_key):
    try:
        configure_gemini(api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        with st.spinner("📤 Enviando vídeo para análise..."):
            video_file = genai.upload_file(path=file_path)
        
        while video_file.state.name == "PROCESSING":
            with st.spinner("⏳ Processando vídeo..."):
                video_file = genai.get_file(video_file.name)
        
        prompt = """
        Você é o Viral Strategist Pro, um especialista em marketing de afiliados.

        Analise este vídeo de produto e forneça:

        1. **PRODUTO**: O que está sendo vendido?
        2. **MELHOR SEGUNDO**: Segundo exato de maior impacto (ex: 00:15)
        3. **GATILHOS**: Gatilhos mentais encontrados (escassez, urgência, curiosidade, prova social)
        4. **POTENCIAL VIRAL**: Nota de 0 a 10
        5. **POSITIVO**: O que funciona bem
        6. **MELHORAR**: O que pode ser melhorado
        7. **ESTRATÉGIA COMPLETA**: YouTube Shorts, Facebook Reels e Shopee Video

        Use marcadores para facilitar a leitura.
        """
        
        with st.spinner("🤖 Gemini analisando..."):
            response = model.generate_content([video_file, prompt])
        genai.delete_file(video_file.name)
        
        return response.text
        
    except Exception as e:
        st.error(f"Erro na análise: {e}")
        return None

def main():
    st.title("🚀 Viral Strategist Pro")
    st.markdown("**Análise de Vídeos com Google Gemini**")
    st.divider()
    
    # === BARRA LATERAL ===
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Verifica se a API Key foi configurada
        if GEMINI_API_KEY == "cole_sua_api_key_aqui":
            st.error("⚠️ API Key não configurada!")
            st.info("""
            **Para configurar:**
            
            1. Edite o arquivo app.py
            2. Na linha 9, cole sua API Key
            3. Faça redeploy
            
            Como obter:
            https://aistudio.google.com/app/apikey
            """)
        else:
            st.success("✅ API Key configurada!")
        
        st.markdown("---")
        st.markdown("""
        ### 📋 Como usar:
        1. Faça upload do vídeo
        2. Clique em analisar
        
        ### 💡 Dicas:
        - Vídeo máx: 100MB
        - Formatos: MP4, MOV, AVI
        """)
    
    # === ÁREA PRINCIPAL ===
    if GEMINI_API_KEY == "cole_sua_api_key_aqui":
        st.stop()
    
    st.subheader("📹 Upload do Vídeo")
    uploaded_file = st.file_uploader(
        "Arraste e solte seu vídeo aqui",
        type=["mp4", "mov", "avi"],
        help="Vídeos de produtos para análise de marketing"
    )
    
    if uploaded_file is not None:
        st.video(uploaded_file)
        
        if st.button("🚀 Analisar Vídeo", type="primary"):
            with st.spinner("💾 Salvando arquivo..."):
                file_path = save_uploaded_file(uploaded_file)
            
            if file_path:
                analysis = analyze_video_with_gemini(file_path, GEMINI_API_KEY)
                if analysis:
                    st.success("✅ Análise concluída!")
                    st.markdown("---")
                    st.subheader("📊 Resultado da Análise")
                    st.markdown(analysis)
                    
                    st.markdown("---")
                    st.subheader("📋 Versão para Copiar")
                    st.code(analysis, language="markdown")

if __name__ == "__main__":
    main()
