"""
Viral Strategist Pro - Análise de Vídeos com Google Gemini
Versão Otimizada para Streamlit Cloud
"""

import streamlit as st
import google.generativeai as genai
import os
import tempfile

st.set_page_config(
    page_title="Viral Strategist Pro",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def configure_gemini(api_key):
    genai.configure(api_key=api_key)

def get_api_key():
    """Obtém a API Key dos secrets ou input do usuário"""
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except:
        return None

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
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        with st.spinner("📤 Enviando vídeo para análise..."):
            video_file = genai.upload_file(path=file_path)
        
        while video_file.state.name == "PROCESSING":
            with st.spinner("⏳ Processando vídeo..."):
                video_file = genai.get_file(video_file.name)
        
        prompt = """
        Você é o Viral Strategist Pro, um especialista em marketing de afiliados.

        Analise este vídeo e forneça:
        1. O que está sendo vendido?
        2. Segundo exato de maior impacto (ex: 00:15)
        3. Gatilhos mentais encontrados
        4. Potencial viral (0-10)
        5. Pontos positivos e de melhoria
        6. Estratégia para YouTube Shorts, Facebook Reels e Shopee Video
        """
        
        with st.spinner("🤖 Gemini analisando..."):
            response = model.generate_content([video_file, prompt])
        genai.delete_file(video_file.name)
        
        return response.text
        
    except Exception as e:
        st.error(f"Erro: {e}")
        return None

def main():
    st.title("🚀 Viral Strategist Pro")
    st.markdown("**Análise de Vídeos com Google Gemini**")
    st.divider()
    
    api_key = get_api_key()
    
    if not api_key:
        st.error("⚠️ API Key não encontrada!")
        st.info("""
        ### Como adicionar a API Key:
        
        **No Streamlit Cloud:**
        1. Vá em Settings → Secrets
        2. Adicione: GOOGLE_API_KEY=sua_chave_aqui
        """)
        return
    
    st.subheader("📹 Upload do Vídeo")
    uploaded_file = st.file_uploader(
        "Arraste e solte seu vídeo",
        type=["mp4", "mov", "avi"],
        help="Vídeos de produtos para análise"
    )
    
    if uploaded_file is not None:
        st.video(uploaded_file)
        
        if st.button("🚀 Analisar Vídeo", type="primary"):
            with st.spinner("💾 Salvando arquivo..."):
                file_path = save_uploaded_file(uploaded_file)
            
            if file_path:
                analysis = analyze_video_with_gemini(file_path, api_key)
                if analysis:
                    st.success("✅ Análise concluída!")
                    st.markdown("---")
                    st.subheader("📊 Resultado")
                    st.markdown(analysis)
                    
                    st.markdown("---")
                    st.subheader("📋 Versão para Copiar")
                    st.code(analysis, language="markdown")

if __name__ == "__main__":
    main()
