import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time

# Configuração da Página
st.set_page_config(page_title="BrendaBot Viral v2", page_icon="🎬", layout="wide")
st.title("🚀 Gerador de Conteúdo Viral Pro")

# Configurar API
API_KEY = "SUA_API_KEY_AQUI" # Lembre-se de usar Secrets no Streamlit Cloud por segurança
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash')

uploaded_file = st.file_uploader("Escolha um vídeo...", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') 
    tfile.write(uploaded_file.read())
    
    st.info("🤖 O Gemini está assistindo seu vídeo... Isso pode levar um momento.")
    
    try:
        # Upload do arquivo para a API do Google
        video_file = genai.upload_file(path=tfile.name, mime_type="video/mp4")
        
        # Aguardar processamento da IA
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
            
        prompt = """
        Atue como um estrategista de vídeo e especialista em SEO de YouTube. Analise o vídeo e retorne:
        1. Um Título Viral (com emojis).
        2. Uma linha com 5 hashtags estratégicas.
        3. Uma Descrição otimizada que inclua um resumo do vídeo.
        4. CAPÍTULOS: Liste os momentos principais no formato '00:00 - Nome do Capítulo'.
        5. CORTES: Sugira 2 ou 3 intervalos de tempo (ex: 00:15 - 00:45) que dariam bons Shorts/TikToks.
        6. COMENTÁRIO: Uma sugestão de pergunta para fixar no topo e gerar debate.
        7. No final, escreva exatamente: 'CAPA: X' (onde X é o melhor segundo do vídeo para uma thumbnail).

        Formate de forma limpa, sem usar as palavras 'TITULO:', 'HASHTAGS:' ou 'DESCRICAO:'.
        """
        
        response = model.generate_content([video_file, prompt])
        texto_ia = response.text
        
        # Interface em Colunas
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📝 Metadados e Estratégia")
            # Removemos a linha da CAPA para o campo de texto limpo
            linhas = texto_ia.split('\n')
            texto_para_copiar = "\n".join([l for l in linhas if "CAPA:" not in l])
            st.text_area("Copiável:", texto_para_copiar, height=450)
        
        with col2:
            # Extrair e mostrar a Capa
            match = re.search(r'CAPA:\s*(\d+)', texto_ia)
            segundo = int(match.group(1)) if match else 1
            
            cap = cv2.VideoCapture(tfile.name)
            cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
            success, frame = cap.read()
            
            if success:
                st.subheader(f"🖼️ Sugestão de Capa (Seg {segundo})")
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                st.image(frame_rgb, use_container_width=True)
            
            cap.release()
            
            st.success("✅ Análise Completa!")
            st.balloons()
        
    except Exception as e:
        st.error(f"Erro detalhado: {e}")
    finally:
        # Limpar arquivo temporário
        if os.path.exists(tfile.name):
            os.remove(tfile.name)
