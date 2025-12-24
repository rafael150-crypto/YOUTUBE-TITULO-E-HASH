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
API_KEY = "SUA_API_KEY_AQUI" 
genai.configure(api_key=API_KEY)

# --- CORREÇÃO DO MODELO ---
# Usamos 'gemini-1.5-flash' que é a versão mais estável e compatível para vídeo
model = genai.GenerativeModel('gemini-1.5-flash')

uploaded_file = st.file_uploader("Escolha um vídeo...", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    # Criar arquivo temporário de forma segura
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tfile:
        tfile.write(uploaded_file.read())
        video_path = tfile.name
    
    st.info("🤖 O Gemini está assistindo seu vídeo... Isso pode levar de 30 a 60 segundos.")
    
    try:
        # Upload do arquivo para a API do Google
        video_file = genai.upload_file(path=video_path)
        
        # Aguardar processamento da IA
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
            
        if video_file.state.name == "FAILED":
            st.error("Erro no processamento do vídeo pela Google.")
            st.stop()

        prompt = """
        Analise o vídeo anexado e atue como um estrategista de YouTube.
        Retorne os seguintes itens de forma organizada:
        
        1. Título Viral (com emojis).
        2. Uma linha com 5 hashtags.
        3. Descrição otimizada (resumo do conteúdo).
        4. CAPÍTULOS: Timestamps no formato '00:00 - Assunto'.
        5. CORTES: 2 sugestões de trechos para Shorts (ex: 00:10 - 00:40).
        6. COMENTÁRIO: Uma pergunta para fixar nos comentários.
        7. No final, escreva exatamente: 'CAPA: X' (X sendo o segundo ideal para a thumbnail).
        
        Não use os rótulos 'TITULO:', 'HASHTAGS:' ou 'DESCRICAO:'.
        """
        
        # Gerar conteúdo
        response = model.generate_content([video_file, prompt])
        texto_ia = response.text
        
        # Interface em Colunas
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📝 Metadados e Estratégia")
            # Removemos a linha da CAPA para o campo de texto limpo
            linhas = texto_ia.split('\n')
            texto_para_copiar = "\n".join([l for l in linhas if "CAPA:" not in l])
            st.text_area("Pronto para copiar:", texto_para_copiar, height=450)
        
        with col2:
            # Extrair e mostrar a Capa usando OpenCV
            match = re.search(r'CAPA:\s*(\d+)', texto_ia)
            segundo = int(match.group(1)) if match else 1
            
            cap = cv2.VideoCapture(video_path)
            # Define a posição do vídeo em milissegundos
            cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
            success, frame = cap.read()
            
            if success:
                st.subheader(f"🖼️ Sugestão de Capa (Segundo {segundo})")
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                st.image(frame_rgb, use_container_width=True)
            else:
                st.warning("Não foi possível extrair o frame para a capa.")
            
            cap.release()
            
            st.success("✅ Análise Completa!")
            st.balloons()
            
            # Botão para limpar o vídeo da API (Boas práticas)
            genai.delete_file(video_file.name)
        
    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")
    finally:
        # Limpar arquivo temporário do sistema local
        if os.path.exists(video_path):
            os.remove(video_path)
