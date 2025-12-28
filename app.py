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

# Configurar API
API_KEY = st.secrets.get("GEMINI_API_KEY", None)

if not API_KEY:
    # Para desenvolvimento local, use secrets ou defina diretamente
    API_KEY = "AIzaSyBPJayL5rgY25x-zkBaZ35GDNop-8VNbt0"

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"Erro ao configurar API: {e}")
    st.stop()

# Modelo padrão
MODEL_NAME = "gemini-1.5-flash"

# Função para upload de vídeo com retry
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

# Função para aguardar processamento com progresso
def wait_for_processing(video_file, max_wait_time=300):
    start_time = time.time()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    while video_file.state.name == "PROCESSING":
        elapsed = time.time() - start_time
        if elapsed > max_wait_time:
            return None, "Timeout: processamento excedeu 5 minutos"
        
        progress = min(elapsed / max_wait_time, 1.0)
        progress_bar.progress(progress)
        status_text.text(f"⏳ Processando vídeo... ({int(elapsed)}s)")
        
        time.sleep(3)
        try:
            video_file = genai.get_file(video_file.name)
        except Exception as e:
            return None, f"Erro ao verificar status: {e}"
    
    progress_bar.empty()
    status_text.empty()
    return video_file, None

# Função para extrair thumbnail com validação
def extract_thumbnail(video_path, target_second):
    try:
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        if target_second > duration:
            target_second = max(1, int(duration / 2))
        
        cap.set(cv2.CAP_PROP_POS_MSEC, target_second * 1000)
        success, frame = cap.read()
        cap.release()
        
        if success:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), None
        return None, "Não foi possível extrair frame"
    except Exception as e:
        return None, str(e)

# Função para extrair segundos da thumbnail
def extract_thumbnail_seconds(text):
    patterns = [
        r'(?:CAPA|Capa|THUMBNAIL|Thumbnail|thumb)\s*[:=]?\s*(\d+)',
        r'(?:melhor|segundo|frame)\s*(?:\w+\s*)?(?:é|e|do)?\s*(\d+)',
        r'(\d{1,2})\s*(?:segundos?|seg|second)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            seconds = int(match.group(1))
            if 1 <= seconds <= 300:
                return seconds
    return None

# Interface principal
uploaded_file = st.file_uploader(
    "📹 Suba o vídeo para validação estratégica...", 
    type=["mp4", "mov", "avi", "mkv", "webm"],
    help="Vídeos de até 2 minutos têm melhor performance."
)

if uploaded_file is not None:
    file_details = {
        "Nome": uploaded_file.name,
        "Tamanho": f"{uploaded_file.size / (1024*1024):.2f} MB",
        "Tipo": uploaded_file.type
    }
    st.sidebar.subheader("📁 Detalhes do Arquivo")
    for key, value in file_details.items():
        st.sidebar.text(f"{key}: {value}")
    
    # Validação de tamanho
    max_size_mb = 50
    if uploaded_file.size > max_size_mb * 1024 * 1024:
        st.error(f"❌ Arquivo muito grande! Máximo permitido: {max_size_mb} MB")
        st.stop()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tfile:
        tfile.write(uploaded_file.read())
        video_path = tfile.name
    
    st.info("🕵️ Analisando riscos e potencial de viralização...")
    
    try:
        # Step 1: Upload do vídeo
        with st.spinner("📤 Fazendo upload do vídeo para análise..."):
            video_file, upload_error = upload_video_with_retry(video_path, "video/mp4")
        
        if upload_error:
            st.error(f"❌ Erro no upload: {upload_error}")
            raise Exception(upload_error)
        
        st.success("✅ Upload concluído!")
        
        # Step 2: Aguardar processamento
        video_file, processing_error = wait_for_processing(video_file)
        
        if processing_error:
            st.error(f"❌ Erro no processamento: {processing_error}")
            raise Exception(processing_error)
        
        if video_file is None:
            st.error("❌ Não foi possível processar o vídeo")
            raise Exception("Vídeo não processado")
        
        st.success("✅ Vídeo processado com sucesso!")
        
        # Step 3: Gerar análise
        prompt = """
        Atue como Especialista em Algoritmo do YouTube e Moderador de Conteúdo. 
        Analise o vídeo e retorne o relatório RIGOROSAMENTE nesta ordem:

        ### 🚨 PAINEL DE VIABILIDADE (LEIA PRIMEIRO)

        1. **RISCO DE RESTRIÇÃO**: (O vídeo viola diretrizes? Tem palavras proibidas, temas sensíveis ou algo que possa causar "Shadowban" ou desmonetização? Dê um status: SEGURO, ARRISCADO ou CRÍTICO).

        2. **CHANCE DE FEED**: (O algoritmo vai distribuir este vídeo no Shorts/Feed? Analise se o conteúdo é original e visualmente atraente para a plataforma).

        3. **VEREDITO DO GANCHO (HOOK)**: (O início prende em 3 segundos? Se não, o vídeo vai 'morrer' cedo. Nota 0-10).

        ### 📈 ANÁLISE DE PERFORMANCE

        4. **POTENCIAL DE VIRALIZAÇÃO**: (0 a 100% e justificativa).

        5. **PONTOS DE ABANDONO**: (Em quais segundos o vídeo fica chato e o público vai sair?).

        ### 📝 ATIVOS DE POSTAGEM (Caso decida postar)

        6. **TÍTULO E HASHTAGS**.

        7. **DESCRIÇÃO SEO**.

        8. **CAPÍTULOS E CORTES**.

        9. **COMENTÁRIO FIXADO**.

        10. **QUOTES PARA REDES SOCIAIS**.

        ### 🌍 TRADUÇÃO

        11. Título e Descrição em Inglês.

        ### 🖼️ THUMBNAIL

        Escreva ao final apenas: 'CAPA: X' (onde X é o melhor segundo para thumbnail, entre 1 e 60 segundos).
        """
        
        with st.spinner("🤖 IA analisando vídeo... Isto pode levar alguns minutos..."):
            # Usa o modelo correto
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content([video_file, prompt])
        
        if not response or not hasattr(response, 'text'):
            st.error("❌ Não foi possível gerar a análise")
            raise Exception("Resposta vazia da API")
        
        texto_ia = response.text
        st.success("✅ Análise concluída!")
        
        # Layout da resposta
        col1, col2 = st.columns([1.2, 0.8])
        
        with col1:
            st.subheader("📋 Relatório Estratégico")
            texto_exibicao = re.sub(r'CAPA:\s*\d+\s*', '', texto_ia, flags=re.IGNORECASE)
            st.markdown(texto_exibicao)
        
        with col2:
            st.subheader("🖼️ Sugestão de Capa")
            
            thumbnail_second = extract_thumbnail_seconds(texto_ia)
            if thumbnail_second is None:
                thumbnail_second = 1
            
            thumbnail, thumb_error = extract_thumbnail(video_path, thumbnail_second)
            
            if thumb_error:
                st.warning(f"⚠️ Não foi possível gerar thumbnail: {thumb_error}")
            else:
                st.image(thumbnail, caption=f"Segundo {thumbnail_second}", use_container_width=True)
                
                ret, buffer = cv2.imencode('.jpg', cv2.cvtColor(thumbnail, cv2.COLOR_RGB2BGR))
                if ret:
                    st.download_button(
                        label="📥 Baixar Capa",
                        data=buffer.tobytes(),
                        file_name=f"thumbnail_{uploaded_file.name.split('.')[0]}.jpg",
                        mime="image/jpeg"
                    )
            
            st.markdown("---")
            st.subheader("⚡ Status de Viabilidade")
            
            risk_level = "SEGURO"
            if re.search(r'\bCRÍTICO\b', texto_ia, re.IGNORECASE):
                risk_level = "CRÍTICO"
                st.error("🚨 **RISCO CRÍTICO**: Este vídeo pode violar diretrizes da plataforma.")
            elif re.search(r'\bARRISCADO\b', texto_ia, re.IGNORECASE):
                risk_level = "ARRISCADO"
                st.warning("⚠️ **RISCO ARRISCADO**: Tome cuidado ao postar este conteúdo.")
            else:
                st.success("✅ **SEGURO**: Este vídeo aparenta estar dentro das diretrizes.")
            
            hook_match = re.search(r'HOOK[:\s]*(\d+(?:[.,]\d+)?)', texto_ia, re.IGNORECASE)
            if hook_match:
                hook_score = float(hook_match.group(1).replace(',', '.'))
                if hook_score < 5:
                    st.warning(f"⚠️ Hook fraco (Nota: {hook_score}/10). Considere refazer os primeiros segundos.")
                elif hook_score >= 8:
                    st.success(f"🎯 Excelente hook! (Nota: {hook_score}/10)")
        
        # Limpar arquivo temporário
        try:
            genai.delete_file(video_file.name)
        except Exception:
            pass  # Se não conseguir deletar, não é crítico
        
    except Exception as e:
        st.error(f"❌ Ocorreu um erro: {type(e).__name__}: {str(e)}")
        with st.expander("Ver detalhes do erro"):
            st.exception(e)
        
    finally:
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
            except:
                pass

else:
    st.info("👆 Por favor, faça o upload de um vídeo para começar a análise.")
    st.markdown("""
    ### Como funciona:
    1. 📹 Faça upload de um vídeo
    2. 🕵️ Nossa IA analisa riscos e potencial de viralização
    3. 📊 Receba um relatório completo com título, hashtags, descrição SEO e thumbnail
    """)
