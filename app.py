import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
from PIL import Image

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="BrendaBot Viral Ultra",
    page_icon="🔥",
    layout="wide"
)

# Estilo CSS para melhorar a aparência
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔥 Validador de Viabilidade e Viralização")
st.subheader("Análise de Conteúdo Estratégico com IA")

# --- CONFIGURAÇÃO DA API ---
# Substitua pela sua chave ou configure nos Secrets do Streamlit
API_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyBPJfcir2lI-HEnbXgTeKUhsPu392f-gv4")

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        st.sidebar.success("✅ Conectado ao Gemini 1.5 Flash")
    except Exception as e:
        st.sidebar.error(f"Erro na API: {e}")
else:
    st.sidebar.warning("⚠️ Insira sua API Key nos Secrets")

# --- FUNÇÕES DE PROCESSAMENTO ---

def process_video_to_frames(video_path, num_frames=15):
    """Abre o vídeo localmente e extrai imagens para evitar erros de codec na nuvem."""
    frames = []
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0
    
    # Seleciona frames distribuídos uniformemente ao longo do vídeo
    interval = total_frames // num_frames
    for i in range(num_frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i * interval)
        ret, frame = cap.read()
        if ret:
            # Converte de BGR (OpenCV) para RGB (PIL/Gemini)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(frame_rgb))
    
    cap.release()
    return frames, duration

# --- INTERFACE PRINCIPAL ---

col_upload, col_info = st.columns([2, 1])

with col_upload:
    uploaded_file = st.file_uploader("📹 Arraste seu vídeo (MP4, MOV, AVI)", type=["mp4", "mov", "avi"])

with col_info:
    st.info("""
    **Como funciona:**
    1. O vídeo é processado frame a frame.
    2. A IA analisa retenção, hook e SEO.
    3. Você recebe o relatório e a sugestão de capa.
    """)

if uploaded_file:
    # Salvar temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tfile:
        tfile.write(uploaded_file.read())
        video_path = tfile.name

    if st.button("🚀 INICIAR ANÁLISE VIRAL"):
        try:
            with st.spinner("📸 Extraindo frames e consultando inteligência artificial..."):
                # Extração
                frames, duration = process_video_to_frames(video_path)
                
                if not frames:
                    st.error("Erro ao ler o arquivo de vídeo. Verifique se o arquivo está corrompido.")
                else:
                    # Prompt Estratégico
                    prompt = f"""
                    Aja como um gestor de canais de YouTube de sucesso e especialista em retenção.
                    Analise esta sequência de frames de um vídeo de {duration:.1f} segundos e responda:

                    ### 🚨 PAINEL DE VIABILIDADE
                    1. **RISCO**: O conteúdo é seguro (Family Friendly)?
                    2. **GANCHO (0-3s)**: O início é visualmente impactante? Nota 0-10.

                    ### 📈 ESTRATÉGIA VIRAL
                    3. **POTENCIAL**: Qual a chance de viralizar (0-100%)?
                    4. **PONTOS FORTES**: O que prenderá a audiência?
                    5. **TÍTULO**: Sugira um título curto e 'curiosity gap'.
                    6. **SEO**: 5 hashtags de alto volume.

                    Indique ao final: CAPA: X (onde X é o número do frame entre 1 e {len(frames)}).
                    """

                    # Chamada da IA enviando a lista de imagens
                    response = model.generate_content([prompt, *frames])
                    
                    # Exibição de Resultados
                    st.markdown("---")
                    res_col1, res_col2 = st.columns([1.5, 1])
                    
                    with res_col1:
                        st.subheader("📋 Relatório Estratégico")
                        st.markdown(response.text)
                    
                    with res_col2:
                        st.subheader("🖼️ Sugestão de Capa")
                        # Lógica simples para pegar o frame sugerido
                        match = re.search(r'CAPA:\s*(\d+)', response.text)
                        idx = int(match.group(1)) - 1 if match else 0
                        idx = max(0, min(idx, len(frames)-1))
                        
                        st.image(frames[idx], caption=f"Frame Sugerido para Thumbnail", use_container_width=True)
                        
                        # Download do frame
                        buffered = tempfile.NamedTemporaryFile(suffix=".jpg")
                        frames[idx].save(buffered.name)
                        with open(buffered.name, "rb") as f:
                            st.download_button("📥 Baixar Imagem da Capa", f.read(), "capa.jpg", "image/jpeg")

        except Exception as e:
            st.error(f"Erro durante a análise: {e}")
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)
else:
    st.write("---")
    st.light("Aguardando upload para iniciar...")
