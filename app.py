import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time

# Configuração da Página
st.set_page_config(page_title="BrendaBot Viral", page_icon="🎬")
st.title("🚀 Gerador de Conteúdo Viral")

# Configurar API (Coloque sua chave entre as aspas)
API_KEY = "AIzaSyDmqVD3ZnaPKumWVrlJUpvWgbZNxNT9unY"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

uploaded_file = st.file_uploader("Escolha um vídeo...", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    # Criar um arquivo temporário para o vídeo
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') 
    tfile.write(uploaded_file.read())
    
    st.info("Analisando o vídeo... Isso pode levar alguns segundos.")
    
    try:
        # CORREÇÃO AQUI: Especificando o mime_type explicitamente
        video_file = genai.upload_file(path=tfile.name, mime_type="video/mp4")
        
        # Aguardar processamento
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
            
        prompt = """
        Atue como especialista em YouTube Shorts. Analise o vídeo e retorne APENAS o texto final para copiar, seguindo esta ordem:
        1. O título viral (com emojis).
        2. Uma linha com as 5 hashtags.
        3. Descriçao completa.
        4. Por último, escreva apenas 'CAPA: X' onde X é o segundo sugerido.
        NÃO use as palavras 'TITULO:', 'HASHTAGS:' ou 'DESCRICAO:'.
        """
        
        response = model.generate_content([video_file, prompt])
        texto_ia = response.text
        
        st.subheader("📝 Sugestão de Postagem")
        
        # Limpar o texto para exibição (remove a linha da CAPA do campo de texto)
        linhas = texto_ia.split('\n')
        texto_para_copiar = "\n".join([l for l in linhas if "CAPA:" not in l])
        st.text_area("Pronto para copiar:", texto_para_copiar, height=200)
        
        # Extrair Capa para mostrar na tela
        match = re.search(r'CAPA:\s*(\d+)', texto_ia)
        segundo = int(match.group(1)) if match else 1
        
        cap = cv2.VideoCapture(tfile.name)
        cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
        success, frame = cap.read()
        
        if success:
            st.subheader(f"🖼️ Sugestão de Capa (Segundo {segundo})")
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            st.image(frame_rgb, use_container_width=True)
            
        cap.release()
        
    except Exception as e:
        st.error(f"Erro detalhado: {e}")
