"""
Viral Strategist Pro - Análise de Vídeos com Google Gemini
Versão com Múltiplos Modelos - Fallback Automático
"""

import streamlit as st
import google.generativeai as genai
import os
import tempfile

# ============================================
# 🔑 COLE SUA API KEY DO GEMINI ABAIXO
# ============================================
# Obtenha em: https://aistudio.google.com/app/apikey
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

def listar_modelos_disponiveis(api_key):
    """Lista os modelos disponíveis para a API Key"""
    try:
        configure_gemini(api_key)
        modelos = genai.list_models()
        return [m.name for m in modelos]
    except Exception as e:
        return None

def analyze_video_with_gemini(file_path, api_key):
    """Tenta analisar vídeo com múltiplos modelos"""
    
    # Lista de modelos a tentar (do mais recente ao mais antigo)
    modelos_a_tentar = [
        "gemini-1.5-pro",
        "gemini-1.5-flash", 
        "gemini-1.0-pro",
        "gemini-pro"
    ]
    
    ultimo_erro = None
    
    for modelo in modelos_a_tentar:
        try:
            configure_gemini(api_key)
            model = genai.GenerativeModel(modelo)
            
            with st.spinner(f"📤 Enviando vídeo para análise (modelo: {modelo})..."):
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
            
            with st.spinner(f"🤖 Gemini analisando com {modelo}..."):
                response = model.generate_content([video_file, prompt])
            genai.delete_file(video_file.name)
            
            return response.text
            
        except Exception as e:
            ultimo_erro = str(e)
            continue
    
    st.error(f"Erro em todos os modelos: {ultimo_erro}")
    return None

def main():
    st.title("🚀 Viral Strategist Pro")
    st.markdown("**Análise de Vídeos com Google Gemini**")
    st.divider()
    
    # Verifica se a API Key foi configurada
    api_key_configurada = GEMINI_API_KEY and GEMINI_API_KEY != "cole_sua_api_key_aqui"
    
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        if api_key_configurada:
            st.success("✅ API Key configurada!")
            st.caption(f"Chave: {GEMINI_API_KEY[:8]}...{GEMINI_API_KEY[-4:]}")
        else:
            st.error("⚠️ API Key não configurada!")
        
        st.markdown("---")
        st.markdown("""
        ### 📋 Como usar:
        1. Configure a API Key
        2. Faça upload do vídeo
        3. Clique em analisar
        
        ### 💡 Dicas:
        - Vídeo máx: 100MB
        - Formatos: MP4, MOV, AVI
        """)
    
    if not api_key_configurada:
        st.error("⚠️ API Key não configurada!")
        
        st.markdown("""
        ### 🔧 Como configurar:

        **1.** Acesse: https://aistudio.google.com/app/apikey
        
        **2.** Clique em "Create API Key"
        
        **3.** Copie a chave (começa com "AIzaSy...")
        
        **4.** Edite o arquivo app.py no GitHub:
        - Entre no seu repositório
        - Clique em app.py
        - Clique no lápis (✏️)
        - Na linha 17, substitua:
        ```python
        GEMINI_API_KEY = "cole_sua_api_key_aqui"
        ```
        Por:
        ```python
        GEMINI_API_KEY = "sua_chave_real_aqui"
        ```
        
        **5.** Commit changes → Deploy no Streamlit
        """)
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
