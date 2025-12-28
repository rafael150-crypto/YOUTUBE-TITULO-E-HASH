import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time

# --- 1. CONFIGURAÇÃO DO SISTEMA ---
st.set_page_config(page_title="BrendaBot Viral Ultra", page_icon="🔥", layout="wide")

st.title("🔥 Validador de Viabilidade e Viralização")
st.caption("Especialista em Games (Minecraft) e Conteúdo Curto")

# Tente usar a chave que você forneceu. 
# DICA: Verifique se não há espaços antes ou depois da chave.
API_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyBPJfcir2lI-HEnbXgTeKUhsPu392f-gv4")

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    st.sidebar.success("✅ API Conectada")
except Exception as e:
    st.sidebar.error(f"❌ Erro na Chave: {e}")

# --- 2. FUNÇÕES DE SUPORTE ---

def wait_for_processing(video_file):
    """Aguarda o processamento do Google com tratamento de erro."""
    with st.status("🎬 IA analisando frames do vídeo...", expanded=True) as status:
        for _ in range(30):  # Máximo 150 segundos
            file = genai.get_file(video_file.name)
            if file.state.name == "PROCESSING":
                time.sleep(5)
            elif file.state.name == "SUCCEEDED":
                status.update(label="✅ Processamento concluído!", state="complete")
                return file
            elif file.state.name == "FAILED":
                status.update(label="❌ Falha no Codec do Vídeo", state="error")
                return None
        return None

def extract_thumbnail(path, sec):
    """Extrai uma imagem do vídeo para a capa."""
    try:
        cap = cv2.VideoCapture(path)
        cap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
        success, frame = cap.read()
        cap.release()
        if success:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except:
        return None
    return None

# --- 3. INTERFACE PRINCIPAL ---

uploaded_file = st.file_uploader("📹 Suba seu vídeo de Minecraft ou Shorts", type=["mp4", "mov", "avi"])

if uploaded_file:
    # Criar arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
        tmp.write(uploaded_file.read())
        video_path = tmp.name

    if st.button("🚀 Iniciar Análise Viral"):
        try:
            # Passo 1: Upload
            st.info("📤 Enviando para análise (nuvem)...")
            video_upload = genai.upload_file(path=video_path)
            
            # Passo 2: Esperar processamento
            processed_file = wait_for_processing(video_upload)

            if processed_file:
                # Passo 3: Prompt Estratégico
                prompt = """
                Aja como um estrategista de YouTube Shorts e TikTok.
                Analise este vídeo (provavelmente gameplay de Minecraft) e responda:
                
                1. **VEREDITO DE VIABILIDADE**: Há risco de restrição por direitos ou diretrizes?
                2. **RETENÇÃO**: O gancho inicial é forte o suficiente para evitar o scroll?
                3. **DICA PARA O CANAL**: O que falta para este vídeo atingir 100k views?
                4. **TÍTULO E TAGS**: 2 sugestões de títulos e 5 hashtags.
                
                Ao final, escreva EXATAMENTE: CAPA: X (onde X é o melhor segundo para a thumbnail).
                """
                
                with st.spinner("🤖 Gerando Relatório Estratégico..."):
                    response = model.generate_content([processed_file, prompt])
                    
                    # Layout de exibição
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.subheader("📋 Auditoria de Conteúdo")
                        st.markdown(response.text)
                    
                    with col2:
                        st.subheader("🖼️ Sugestão de Capa")
                        match = re.search(r'CAPA:\s*(\d+)', response.text)
                        seg = int(match.group(1)) if match else 1
                        img = extract_thumbnail(video_path, seg)
                        if img is not None:
                            st.image(img, use_container_width=True)
                            
                            # Botão de Download da Capa
                            ret, buffer = cv2.imencode('.jpg', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                            st.download_button("📥 Baixar Capa", buffer.tobytes(), "capa_viral.jpg", "image/jpeg")

                # Passo 4: Limpeza
                genai.delete_file(video_upload.name)
            else:
                st.error("⚠️ O Google não conseguiu processar este arquivo de vídeo. Tente converter o vídeo para um formato MP4 mais leve ou use um clipe mais curto.")

        except Exception as e:
            st.error(f"❌ Erro crítico: {e}")
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)
else:
    st.info("👆 Selecione um arquivo de vídeo para começar.")

# --- 4. RODAPÉ ---
st.markdown("---")
st.markdown("⚡ **Dica para Minecraft:** Se o erro persistir, reduza a resolução da gravação para 1080p a 30fps.")
