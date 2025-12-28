import streamlit as st
import google.generativeai as genai
import cv2
import os
import tempfile
import numpy as np
from PIL import Image

# 1. Configuração Inicial
st.set_page_config(page_title="BrendaBot Ultra Fix", page_icon="🔥")

st.title("🔥 Validador Viral - Modo de Segurança")

# 2. Configuração da Chave (Verifique se a sua chave está ativa)
# DICA: Tente criar uma chave NOVA no AI Studio se o erro persistir.
API_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyBPJfcir2lI-HEnbXgTeKUhsPu392f-gv4")

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    st.sidebar.success("✅ Conexão com Google IA: OK")
except Exception as e:
    st.sidebar.error(f"Erro de Configuração: {e}")
    st.stop()

# 3. Upload do Ficheiro
uploaded_file = st.file_uploader("Suba o vídeo aqui", type=["mp4", "mov", "avi"])

if uploaded_file:
    # Guardar o vídeo num ficheiro temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tfile:
        tfile.write(uploaded_file.read())
        temp_path = tfile.name

    if st.button("ANALISAR AGORA"):
        try:
            # EXTRAÇÃO SIMPLIFICADA DE FRAMES
            st.info("🔄 A processar vídeo...")
            video = cv2.VideoCapture(temp_path)
            
            frames_para_ai = []
            count = 0
            
            # Tenta ler apenas 5 frames para garantir que não estoura a memória
            while len(frames_para_ai) < 5 and count < 100:
                success, image = video.read()
                if not success:
                    break
                if count % 20 == 0: # Pega um frame a cada 20
                    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    frames_para_ai.append(Image.fromarray(img_rgb))
                count += 1
            video.release()

            if not frames_para_ai:
                st.error("❌ O sistema não conseguiu ler os frames do vídeo. O formato pode ser incompatível.")
            else:
                st.info("🤖 A consultar a Inteligência Artificial...")
                
                # Prompt Minimalista para testar
                prompt = "Analise estas imagens de um vídeo e diga: 1. O que acontece no vídeo? 2. Qual o potencial de viralização?"
                
                response = model.generate_content([prompt, *frames_para_ai])
                
                st.success("✅ Análise Concluída!")
                st.markdown(response.text)
                
                # Mostrar os frames capturados para confirmar que funcionou
                st.subheader("Frames Analisados:")
                st.image(frames_para_ai, width=150)

        except Exception as e:
            st.error(f"❌ Erro Crítico: {str(e)}")
            st.warning("Se o erro for 'API_KEY_INVALID', a sua chave expirou ou foi bloqueada.")
        
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

else:
    st.info("Aguardando upload de vídeo para teste.")
