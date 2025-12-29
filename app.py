"""
Viral Strategist Pro - Análise de Vídeos com Google Gemini
Desenvolvido para Streamlit + GitHub Deployment
"""

import streamlit as st
import google.generativeai as genai
import os
import tempfile
from pathlib import Path

# ============================================
# CONFIGURAÇÕES DA PÁGINA
# ============================================
st.set_page_config(
    page_title="Viral Strategist Pro",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ============================================
# CONFIGURAÇÃO DA API DO GEMINI
# ============================================
def configure_gemini(api_key: str):
    """Configura a API do Google Gemini"""
    genai.configure(api_key=api_key)

# ============================================
# FUNÇÕES PRINCIPAIS
# ============================================
def save_uploaded_file(uploaded_file) -> str:
    """Salva o arquivo上传 em um arquivo temporário"""
    try:
        # Cria diretório temporário se não existir
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, uploaded_file.name)
        
        # Salva o arquivo
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    except Exception as e:
        st.error(f"Erro ao salvar arquivo: {e}")
        return None

def analyze_video_with_gemini(file_path: str, api_key: str) -> str:
    """Analisa o vídeo usando o Google Gemini"""
    try:
        # Configura a API
        configure_gemini(api_key)
        
        # Carrega o modelo Gemini 1.5 Pro (suporta vídeo)
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        # Faz upload do arquivo para o Gemini
        st.info("📤 Enviando vídeo para análise...")
        video_file = genai.upload_file(path=file_path)
        
        # Aguarda o processamento do vídeo
        while video_file.state.name == "PROCESSING":
            st.info("⏳ Processando vídeo...")
            video_file = genai.get_file(video_file.name)
        
        # Prompt de análise especializada
        prompt = """
        Você é o Viral Strategist Pro, um especialista em marketing de afiliados e análise de vídeos curtos.

        Analise este vídeo de produto e forneça:

        1. **ANÁLISE DO PRODUTO**: O que está sendo vendido? Qual problema resolve?
        
        2. **MOMENTO DE MAIOR IMPACTO**: Identifique o segundo exato (ex: 00:15) onde há maior desejo de compra
        
        3. **GATILHOS ENCONTRADOS**: Liste os gatilhos mentais usados (escassez, urgência, curiosidade, prova social, etc.)
        
        4. **PONTOS POSITIVOS**: O que funciona bem neste vídeo?
        
        5. **PONTOS DE MELHORIA**: O que pode ser melhorado?
        
        6. **POTENCIAL VIRAL**: De 0 a 10, qual o potencial de viralização?
        
        7. **TARGET**: Qual o público-alvo provável?
        
        Seja detalhado mas objetivo. Use marcadores para facilitar a leitura.
        """
        
        # Gera a resposta
        st.info("🤖 Gemini analisando vídeo...")
        response = model.generate_content([video_file, prompt])
        
        # Remove o arquivo temporário
        genai.delete_file(video_file.name)
        
        return response.text
        
    except Exception as e:
        st.error(f"Erro na análise: {e}")
        return None

# ============================================
# INTERFACE DO APP
# ============================================
def main():
    """Função principal da aplicação"""
    
    # Header
    st.title("🚀 Viral Strategist Pro")
    st.markdown("**Análise de Vídeos com Google Gemini**")
    st.divider()
    
    # Sidebar - Configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Input da API Key
        api_key = st.text_input(
            "🔑 Google API Key",
            type="password",
            help="Obtenha sua chave em: https://aistudio.google.com/app/apikey"
        )
        
        st.markdown("---")
        
        # Instruções
        st.markdown("""
        ### 📋 Como usar:
        
        1. Insira sua API Key do Google
        2. Faça upload do vídeo
        3. Aguarde a análise do Gemini
        4. Copie a estratégia!
        
        ### 💡 Dicas:
        - Formatos: MP4, MOV, AVI
        - Tamanho máx: 100MB
        - Duração: até 2 minutos
        """)
    
    # Área principal - Upload
    st.subheader("📹 Upload do Vídeo")
    
    uploaded_file = st.file_uploader(
        "Arraste e solte seu vídeo aqui",
        type=["mp4", "mov", "avi"],
        help="Vídeos de produtos para análise de marketing"
    )
    
    # Botão de análise
    if uploaded_file is not None:
        st.video(uploaded_file)
        
        if st.button("🚀 Analisar Vídeo", type="primary"):
            if not api_key:
                st.error("⚠️ Por favor, insira sua API Key do Google Gemini!")
            else:
                # Salva o arquivo temporário
                with st.spinner("💾 Salvando arquivo..."):
                    file_path = save_uploaded_file(uploaded_file)
                
                if file_path:
                    # Realiza a análise
                    analysis = analyze_video_with_gemini(file_path, api_key)
                    
                    if analysis:
                        # Exibe o resultado
                        st.success("✅ Análise concluída!")
                        st.markdown("---")
                        st.subheader("📊 Resultado da Análise")
                        st.markdown(analysis)
                        
                        # Botão para copiar
                        st.code(analysis, language="markdown")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>Desenvolvido com ❤️ usando Streamlit + Google Gemini</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
