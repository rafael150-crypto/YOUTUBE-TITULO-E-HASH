import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile

# Configuração da Página
st.set_page_config(page_title="BrendaBot Viral", page_icon="🎬")
st.title("🚀 Gerador de Conteúdo Viral")

# Configurar API
API_KEY = "AIzaSyCVtbBNnoqftmf8dZ5otTErswiBnYK7XZ0"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

uploaded_file = st.file_uploader("Escolha um vídeo...", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    # Criar um arquivo temporário para o vídeo
    tfile = tempfile.NamedTemporaryFile(delete=False) 
    tfile.write(uploaded_file.read())
    
    st.info("Analisando o vídeo... Isso pode levar alguns segundos.")
    
    try:
        # Enviar para o Gemini
        video_file = genai.upload_file(path=tfile.name)
        
        # Aguardar processamento
        import time
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
            
        prompt = "Analise o vídeo para YouTube Shorts. Retorne: O Título viral (com emojis), as 5 hashtags, a descrição curta e 'CAPA: X' (segundo sugerido). Sem rótulos extras."
        response = model.generate_content([video_file, prompt])
        
        # Exibir Texto
        texto_ia = response.text
        st.subheader("📝 Sugestão de Postagem")
        
        # Limpar o texto para o usuário copiar
        linhas = texto_ia.split('\n')
        texto_limpo = "\n".join([l for l in linhas if "CAPA:" not in l])
        st.text_area("Copie aqui:", texto_limpo, height=150)
        
        # Extrair Capa
        match = re.search(r'CAPA:\s*(\d+)', texto_ia)
        segundo = int(match.group(1)) if match else 1
        
        cap = cv2.VideoCapture(tfile.name)
        cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
        success, frame = cap.read()
        
        if success:
            st.subheader("🖼️ Sugestão de Capa")
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            st.image(frame_rgb)
            
        cap.release()
        
    except Exception as e:
        st.error(f"Erro: {e}")
