import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time

# Configuração da Página
st.set_page_config(page_title="BrendaBot Viral", page_icon="🎬", layout="wide")
st.title("🚀 Gerador de Conteúdo Viral")

# Configurar API - Mantendo exatamente como você usava
API_KEY = "AIzaSyDmqVD3ZnaPKumWVrlJUpvWgbZNxNT9unY"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

uploaded_file = st.file_uploader("Escolha um vídeo...", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    # Criar um arquivo temporário para o vídeo
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') 
    tfile.write(uploaded_file.read())
    video_path = tfile.name
    
    st.info("Analisando o vídeo... Isso pode levar alguns segundos.")
    
    try:
        # Upload do arquivo para a IA
        video_file = genai.upload_file(path=video_path, mime_type="video/mp4")
        
        # Aguardar processamento
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
            
        # PROMPT ATUALIZADO COM AS NOVAS FUNÇÕES
        prompt = """
        Atue como especialista em YouTube Shorts e estrategista de retenção. 
        Analise o vídeo e retorne o texto seguindo esta ordem:
        
        1. O título viral (com emojis).
        2. Uma linha com as 5 hashtags.
        3. Descrição completa.
        4. CAPÍTULOS: Gere a minutagem (ex: 00:05 - Início impactante).
        5. CORTES: Sugira 2 momentos para Shorts/TikTok (ex: 00:10 a 00:40).
        6. COMENTÁRIO: Uma pergunta para fixar no topo e gerar engajamento.
        7. Por último, escreva apenas 'CAPA: X' onde X é o segundo sugerido.
        
        NÃO use as palavras 'TITULO:', 'HASHTAGS:' ou 'DESCRICAO:'.
        """
        
        response = model.generate_content([video_file, prompt])
        texto_ia = response.text
        
        # Divisão da tela para melhor visualização
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📝 Conteúdo Gerado")
            # Limpar o texto para exibição (remove a linha da CAPA do campo de texto)
            linhas = texto_ia.split('\n')
            texto_para_copiar = "\n".join([l for l in linhas if "CAPA:" not in l])
            st.text_area("Pronto para copiar:", texto_para_copiar, height=400)
        
        with col2:
            # Extrair Capa para mostrar na tela
            match = re.search(r'CAPA:\s*(\d+)', texto_ia)
            segundo = int(match.group(1)) if match else 1
            
            cap = cv2.VideoCapture(video_path)
            cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
            success, frame = cap.read()
            
            if success:
                st.subheader(f"🖼️ Sugestão de Capa (Segundo {segundo})")
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                st.image(frame_rgb, use_container_width=True)
            
            cap.release()
            st.success("Análise concluída com sucesso!")
        
        # Limpeza na API da Google
        genai.delete_file(video_file.name)
        
    except Exception as e:
        st.error(f"Erro detalhado: {e}")
    finally:
        # Remover o arquivo temporário local
        if os.path.exists(video_path):
            os.remove(video_path)
