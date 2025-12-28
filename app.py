import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="BrendaBot Viral Ultra", 
    page_icon="🔥", 
    layout="wide"
)

st.title("🔥 Validador de Viabilidade e Viralização")
st.markdown("---")

# --- CONFIGURAÇÃO DE API ---
# Substitua pela sua chave válida nos Secrets ou deixe o campo de input
API_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyBPJfcir2lI-HEnbXgTeKUhsPu392f-gv4")

try:
    genai.configure(api_key=API_KEY)
    # Gemini 1.5 Flash é o modelo recomendado para processamento rápido de vídeo
    model = genai.GenerativeModel("gemini-1.5-flash")
    st.sidebar.success("✅ Conectado ao Gemini 1.5 Flash")
except Exception as e:
    st.sidebar.error(f"❌ Erro de Conexão: {e}")

# --- FUNÇÕES TÉCNICAS ---

def wait_for_processing(video_file):
    """Aguarda o Google processar o vídeo antes de permitir a análise."""
    with st.status("🎬 IA está processando os frames do vídeo...", expanded=True) as status:
        while True:
            try:
                file = genai.get_file(video_file.name)
                if file.state.name == "PROCESSING":
                    time.sleep(5)
                elif file.state.name == "SUCCEEDED":
                    status.update(label="✅ Vídeo pronto para análise!", state="complete")
                    return file
                elif file.state.name == "FAILED":
                    status.update(label="❌ O Google falhou ao processar este arquivo.", state="error")
                    return None
            except Exception as e:
                st.error(f"Erro ao verificar status: {e}")
                return None

def extract_thumbnail(path, sec):
    """Extrai um frame específico do vídeo usando OpenCV."""
    try:
        cap = cv2.VideoCapture(path)
        # Define o tempo em milissegundos
        cap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
        success, frame = cap.read()
        cap.release()
        if success:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except:
        return None
    return None

# --- INTERFACE DE USUÁRIO ---

uploaded_file = st.file_uploader("📹 Suba seu vídeo (Minecraft, Shorts, Reels...)", type=["mp4", "mov", "avi"])

if uploaded_file:
    # Salva o vídeo temporariamente para o OpenCV e para Upload
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
        tmp.write(uploaded_file.read())
        video_path = tmp.name

    if st.button("🚀 Iniciar Auditoria Estratégica"):
        try:
            # 1. Upload para o Google
            st.info("📤 Fazendo upload para os servidores de IA...")
            video_upload = genai.upload_file(path=video_path)
            
            # 2. Aguarda processamento
            processed_file = wait_for_processing(video_upload)

            if processed_file:
                # 3. Prompt de Análise Profunda
                prompt = """
                Aja como um Diretor de Criação e Especialista em Algoritmos de Redes Sociais.
                Analise este vídeo e forneça um relatório detalhado:

                1. **VEREDITO DE VIABILIDADE**: O vídeo é seguro para monetização ou corre risco de restrição?
                2. **ANÁLISE DO GANCHO (HOOK)**: Os primeiros 3 segundos prendem a atenção? Como melhorar?
                3. **POTENCIAL VIRAL**: De 0 a 100%, qual a chance de viralizar no Shorts/TikTok?
                4. **PONTOS CRÍTICOS**: Em quais momentos o vídeo fica monótono e perde retenção?
                5. **ESTRATÉGIA DE POSTAGEM**: Sugira 2 títulos magnéticos e as melhores hashtags.
                
                Ao final, escreva obrigatoriamente neste formato: CAPA: X (onde X é o segundo ideal para a thumbnail).
                """
                
                with st.spinner("🤖 IA analisando conteúdo e gerando insights..."):
                    response = model.generate_content([processed_file, prompt])
                
                # Exibição dos resultados em colunas
                col1, col2 = st.columns([1.5, 1])
                
                with col1:
                    st.subheader("📋 Relatório BrendaBot")
                    st.markdown(response.text)
                
                with col2:
                    st.subheader("🖼️ Sugestão de Capa")
                    # Busca o número após "CAPA:" no texto da resposta
                    match = re.search(r'CAPA:\s*(\d+)', response.text)
                    segundo = int(match.group(1)) if match else 1
                    
                    img = extract_thumbnail(video_path, segundo)
                    if img is not None:
                        st.image(img, caption=f"Frame sugerido no segundo {segundo}")
                        
                        # Botão de Download da Capa
                        ret, buffer = cv2.imencode('.jpg', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                        st.download_button("📥 Baixar Thumbnail", buffer.tobytes(), "thumbnail.jpg", "image/jpeg")
                
                # Limpa o arquivo do servidor do Google após análise
                genai.delete_file(video_upload.name)
            
        except Exception as e:
            st.error(f"❌ Ocorreu um erro inesperado: {e}")
        finally:
            # Remove o arquivo temporário do seu computador/servidor
            if os.path.exists(video_path):
                os.remove(video_path)

else:
    st.info("Aguardando vídeo para começar. Dica: Vídeos com menos de 200MB funcionam melhor.")

# Rodapé informativo
st.markdown("---")
st.caption("BrendaBot Viral Ultra - Powered by Gemini 1.5 Flash")
