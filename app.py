import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time

# Configuração da Página
st.set_page_config(
    page_title="BrendaBot Viral Ultra", 
    page_icon="🔥", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔥 Validador de Viabilidade e Viralização")
st.markdown("---")

# --- CONFIGURAÇÃO DE API SEGURA ---
# Tenta pegar dos secrets do Streamlit
API_KEY = st.secrets.get("GEMINI_API_KEY", None)

if not API_KEY:
    st.warning("⚠️ Chave de API não configurada nos Secrets. Por favor, insira manualmente para testar:")
    API_KEY = st.text_input("AIzaSyBPJayL5rgY25x-zkBaZ35GDNop-8VNbt0", type="password")
    if not API_KEY:
        st.stop()

genai.configure(api_key=API_KEY)

# Lista de modelos reais (Gemini 1.5 é o padrão atual para vídeo)
# O 1.5-flash é mais rápido e ideal para o Streamlit não travar
VALID_MODELS = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]
MODEL_NAME = None

for model_id in VALID_MODELS:
    try:
        # Teste de conexão simples
        model_test = genai.GenerativeModel(model_id)
        MODEL_NAME = model_id
        st.sidebar.success(f"✅ Conectado ao modelo: {MODEL_NAME}")
        break
    except Exception:
        continue

if not MODEL_NAME:
    st.error("❌ Erro: Nenhum modelo disponível. Verifique sua chave de API.")
    st.stop()

# --- FUNÇÕES DE SUPORTE ---

def upload_video_with_retry(path, mime_type, max_retries=3):
    for attempt in range(max_retries):
        try:
            video_file = genai.upload_file(path=path, mime_type=mime_type)
            return video_file, None
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return None, str(e)
    return None, "Máximo de tentativas excedido"

def wait_for_processing(video_file, max_wait_time=300):
    start_time = time.time()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > max_wait_time:
            return None, "Timeout: processamento excedeu 5 minutos"
        
        # Recarregar status do arquivo
        current_file = genai.get_file(video_file.name)
        
        if current_file.state.name == "PROCESSING":
            progress = min(elapsed / max_wait_time, 1.0)
            progress_bar.progress(progress)
            status_text.text(f"⏳ IA Processando vídeo... ({int(elapsed)}s)")
            time.sleep(5)
        elif current_file.state.name == "FAILED":
            return None, "O processamento do vídeo falhou nos servidores do Google."
        else:
            break
    
    progress_bar.empty()
    status_text.empty()
    return current_file, None

def extract_thumbnail(video_path, target_second):
    try:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps) if fps > 0 else 0
        
        if target_second > duration:
            target_second = max(1, duration // 2)
            
        cap.set(cv2.CAP_PROP_POS_MSEC, target_second * 1000)
        success, frame = cap.read()
        cap.release()
        
        if success:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), None
        return None, "Erro ao capturar frame"
    except Exception as e:
        return None, str(e)

def extract_thumbnail_seconds(text):
    match = re.search(r'CAPA:\s*(\d+)', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 1

# --- INTERFACE PRINCIPAL ---

uploaded_file = st.file_uploader("📹 Suba o vídeo para análise estratégica", type=["mp4", "mov", "avi"])

if uploaded_file:
    # Salvar arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tfile:
        tfile.write(uploaded_file.read())
        video_path = tfile.name

    st.info("🚀 Iniciando análise profunda...")

    try:
        # 1. Upload
        video_file, err = upload_video_with_retry(video_path, "video/mp4")
        if err: st.error(err); st.stop()

        # 2. Processamento
        video_file, err = wait_for_processing(video_file)
        if err: st.error(err); st.stop()

        # 3. Análise com Prompt Otimizado
        prompt = """
        Analise este vídeo como um Diretor de Criação e Especialista em Viralização.
        
        ### 🚨 PAINEL DE VIABILIDADE
        1. RISCO DE RESTRIÇÃO: (SEGURO, ARRISCADO ou CRÍTICO). Cite elementos visuais ou falas sensíveis.
        2. CHANCE DE FEED: Avalie a qualidade técnica (iluminação, áudio e enquadramento).
        3. VEREDITO DO GANCHO: Nota 0-10 para os primeiros 3 segundos.

        ### 📈 ANÁLISE DE PERFORMANCE
        4. POTENCIAL DE VIRALIZAÇÃO: % de chance de viralizar.
        5. RETENÇÃO: Em quais segundos há risco de o usuário pular o vídeo?

        ### 📝 ATIVOS DE POSTAGEM
        6. TÍTULO MAGNÉTICO E HASHTAGS.
        7. DESCRIÇÃO SEO OTIMIZADA.
        8. COMENTÁRIO FIXADO (CTA).

        ### 🖼️ THUMBNAIL
        Indique o melhor momento para a capa escrevendo exatamente: CAPA: X (onde X é o segundo).
        """

        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content([video_file, prompt])
        
        # Exibição dos Resultados
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            st.subheader("📋 Relatório Estratégico")
            st.markdown(response.text)

        with col2:
            st.subheader("🖼️ Sugestão de Capa")
            segundo = extract_thumbnail_seconds(response.text)
            thumb, err_thumb = extract_thumbnail(video_path, segundo)
            if thumb is not None:
                st.image(thumb, caption=f"Sugestão no segundo {segundo}")
            
            # Botão de download para a capa
            if thumb is not None:
                ret, buffer = cv2.imencode('.jpg', cv2.cvtColor(thumb, cv2.COLOR_RGB2BGR))
                st.download_button("📥 Baixar Capa", buffer.tobytes(), "capa.jpg", "image/jpeg")

        # Limpeza no Google (importante para não gastar armazenamento)
        genai.delete_file(video_file.name)

    except Exception as e:
        st.error(f"Erro inesperado: {e}")
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

else:
    st.info("Aguardando upload de vídeo...")
