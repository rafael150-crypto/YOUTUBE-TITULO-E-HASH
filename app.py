import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
from PIL import Image

# --- CONFIGURAÇÃO DE SEGURANÇA ---
# O Streamlit busca automaticamente GEMINI_API_KEY nos Secrets ou Variáveis de Ambiente
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Erro de Segurança: Chave de API não configurada.")
    st.info("Configure a chave nos 'Secrets' do Streamlit Cloud ou no arquivo '.streamlit/secrets.toml' localmente.")
    st.stop()

# Configuração da API sem expor a chave no log
genai.configure(api_key=api_key)

# --- INTERFACE ---
st.set_page_config(page_title="BrendaBot Viral Ultra", page_icon="🔥", layout="wide")

st.title("🔥 Validador de Viabilidade e Viralização")
st.caption("Análise estratégica de Gameplay e Shorts via Gemini 1.5 Flash")

# --- FUNÇÕES ---
def extrair_frames(video_path, qtd=12):
    """Extrai frames para análise multimodal segura."""
    frames = []
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0: return None
    
    for i in range(qtd):
        cap.set(cv2.CAP_PROP_POS_FRAMES, (total // qtd) * i)
        success, frame = cap.read()
        if success:
            # Converte para RGB e depois para objeto PIL Image
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            frames.append(img)
    cap.release()
    return frames

# --- FLUXO PRINCIPAL ---
uploaded_file = st.file_uploader("📹 Suba seu vídeo para análise", type=["mp4", "mov", "avi"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
        tmp.write(uploaded_file.read())
        video_path = tmp.name

    if st.button("🚀 Iniciar Auditoria Estratégica"):
        try:
            with st.spinner("📸 Processando frames e consultando IA..."):
                # 1. Extração de frames (Bypass de erro de codec)
                lista_frames = extrair_frames(video_path)
                
                if not lista_frames:
                    st.error("Não foi possível ler o vídeo. Verifique o formato.")
                    st.stop()

                # 2. Configuração do Modelo
                model = genai.GenerativeModel('models/gemini-1.5-flash')

                # 3. Prompt de Especialista
                prompt = """
                Aja como um Estrategista de Viralização e Moderador de Conteúdo.
                Analise esta sequência de imagens do vídeo e forneça:

                1. **VEREDITO DE SEGURANÇA**: O vídeo infringe diretrizes (violência, linguagem, etc)?
                2. **ANÁLISE DO GANCHO (HOOK)**: Os primeiros frames são impactantes?
                3. **POTENCIAL DE FEED**: Qual a chance (0-100%) de retenção no Shorts/TikTok?
                4. **TÍTULO E SEO**: Sugira um título 'clickbait do bem' e 5 hashtags.
                
                Ao final, retorne: CAPA: X (onde X é o número do frame sugerido entre 1 e 12).
                """

                # Envio multimodal (Texto + Lista de Imagens)
                response = model.generate_content([prompt, *lista_frames])

                # 4. Exibição dos Resultados
                st.divider()
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("📋 Relatório BrendaBot")
                    st.markdown(response.text)
                
                with col2:
                    st.subheader("🖼️ Sugestão de Capa")
                    match = re.search(r'CAPA:\s*(\d+)', response.text)
                    idx = int(match.group(1)) - 1 if match else 0
                    idx = max(0, min(idx, len(lista_frames)-1))
                    st.image(lista_frames[idx], use_container_width=True, caption=f"Frame Sugerido #{idx+1}")

        except Exception as e:
            st.error(f"Erro na análise: {e}")
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)

else:
    st.info("Aguardando upload de vídeo.")
