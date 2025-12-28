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
    layout="wide"
)

st.title("🔥 Validador de Viabilidade e Viralização")
st.markdown("---")

# --- CONFIGURAÇÃO DE API ---
# Tenta pegar dos secrets, se não, usa a que você forneceu
API_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyBPJfcir2lI-HEnbXgTeKUhsPu392f-gv4")

try:
    genai.configure(api_key=API_KEY)
    # Usando o modelo 1.5-flash que é o mais estável para análise de vídeo
    model = genai.GenerativeModel("gemini-1.5-flash")
    st.sidebar.success("✅ API Conectada: Gemini 1.5 Flash")
except Exception as e:
    st.error(f"Erro na conexão: {e}")
    st.stop()

# --- FUNÇÕES ---

def wait_for_processing(video_file):
    with st.status("🎬 Processando vídeo na IA...", expanded=True) as status:
        while True:
            file = genai.get_file(video_file.name)
            if file.state.name == "PROCESSING":
                time.sleep(5)
            elif file.state.name == "SUCCEEDED":
                status.update(label="✅ Vídeo pronto para análise!", state="complete")
                return file
            else:
                status.update(label="❌ Erro no processamento", state="error")
                return None

def extract_thumbnail(path, sec):
    cap = cv2.VideoCapture(path)
    cap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
    success, frame = cap.read()
    cap.release()
    if success:
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return None

# --- UI ---

uploaded_file = st.file_uploader("📹 Arraste seu vídeo aqui", type=["mp4", "mov", "avi"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
        tmp.write(uploaded_file.read())
        video_path = tmp.name

    if st.button("🚀 Iniciar Auditoria Viral"):
        try:
            # Upload para o Google
            video_upload = genai.upload_file(path=video_path)
            processed_file = wait_for_processing(video_upload)

            if processed_file:
                # PROMPT ULTRA OTIMIZADO
                prompt = """
                Aja como um estrategista de conteúdo viral (MrBeast style) e especialista em algoritmos.
                Analise o vídeo e forneça:

                1. **STATUS DE SEGURANÇA**: (SEGURO/ARRISCADO) - Analise diretrizes da comunidade.
                2. **RETENÇÃO INICIAL (0-3s)**: Como está o gancho visual e auditivo? Nota 0-10.
                3. **QUALIDADE TÉCNICA**: Iluminação, áudio e enquadramento estão profissionais?
                4. **PONTOS DE FUGA**: Exatamente em que segundo o vídeo fica lento?
                5. **ESTRATÉGIA DE POSTAGEM**: Sugira 3 Títulos Curtos (curiosidade, medo, desejo) e 5 Hashtags.
                6. **SEO**: Uma descrição de 2 linhas focada em busca.
                
                Ao final, escreva exatamente: CAPA: X (substitua X pelo melhor segundo entre 1 e 10 para a thumbnail).
                """
                
                response = model.generate_content([processed_file, prompt])
                
                # Layout de Resultados
                col1, col2 = st.columns([1.5, 1])
                
                with col1:
                    st.subheader("📊 Relatório de Viabilidade")
                    st.markdown(response.text)
                
                with col2:
                    st.subheader("🖼️ Sugestão de Capa")
                    match = re.search(r'CAPA:\s*(\d+)', response.text)
                    segundo = int(match.group(1)) if match else 1
                    
                    img = extract_thumbnail(video_path, segundo)
                    if img is not None:
                        st.image(img, caption=f"Frame ideal no segundo {segundo}")
                        
                # Limpeza
                genai.delete_file(video_upload.name)
        
        except Exception as e:
            st.error(f"Erro: {e}")
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)

# --- INSTRUÇÕES ---
else:
    st.info("Dica: Vídeos curtos (até 60s) são processados mais rápido e têm melhor análise de retenção.")
