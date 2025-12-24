import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time

# Configuração da Página
st.set_page_config(page_title="BrendaBot Viral Ultra", page_icon="🔥", layout="wide")
st.title("🔥 QG de Viralização - BrendaBot Ultra")

# Configurar API
API_KEY = "AIzaSyCiJyxLVYVgI7EiTuQmkQGTi1nWiQn9g_8"
genai.configure(api_key=API_KEY)

# Mantendo o modelo que você confirmou que funciona
model = genai.GenerativeModel('models/gemini-2.5-flash')

uploaded_file = st.file_uploader("Escolha um vídeo...", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') 
    tfile.write(uploaded_file.read())
    video_path = tfile.name
    
    st.info("🚀 BrendaBot está fazendo uma auditoria completa do seu vídeo...")
    
    try:
        # Upload do arquivo para a IA
        video_file = genai.upload_file(path=video_path, mime_type="video/mp4")
        
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
            
        # PROMPT ULTRA AVANÇADO
        prompt = """
        Atue como um Diretor de Conteúdo e Especialista em Algoritmos de Redes Sociais. 
        Analise o vídeo e retorne um relatório estruturado exatamente assim:

        ### 🎯 ANÁLISE DE PERFORMANCE
        1. **POTENCIAL DE VIRALIZAÇÃO**: (Dê uma nota de 0 a 100% e explique o porquê).
        2. **QUALIDADE DO GANCHO (HOOK)**: (Analise os primeiros 5 segundos. O espectador vai parar de rolar a tela? Como melhorar?).
        3. **PONTOS DE RETENÇÃO**: (Em quais momentos o vídeo fica lento e as pessoas podem sair?).

        ### 📝 CONTEÚDO PARA POSTAGEM
        4. **TÍTULO E HASHTAGS**: (Sugestão viral com emojis).
        5. **DESCRIÇÃO SEO**: (Texto otimizado para busca).
        6. **COMENTÁRIO FIXADO**: (Pergunta para gerar debate).

        ### ✂️ ESTRATÉGIA DE REPURPOSING
        7. **CAPÍTULOS**: (Timestamps 00:00 - Assunto).
        8. **CORTES PARA SHORTS**: (Sugira tempos exatos para extrair pequenos vídeos virais).
        9. **QUOTES MAGNÉTICAS**: (As 3 frases mais impactantes ditas no vídeo para usar em legendas).

        ### 🌍 EXPANSÃO GLOBAL
        10. **INGLÊS**: (Traduza o Título e a Descrição para o Inglês).

        ### 🖼️ THUMBNAIL
        11. Escreva ao final apenas: 'CAPA: X' (onde X é o melhor segundo do vídeo para a capa).
        """
        
        response = model.generate_content([video_file, prompt])
        texto_ia = response.text
        
        # Interface em duas colunas
        col1, col2 = st.columns([1.2, 0.8])
        
        with col1:
            st.subheader("📊 Auditoria de Conteúdo")
            # Exclui apenas a tag de CAPA da área de texto principal
            texto_exibicao = re.sub(r'CAPA:\s*\d+', '', texto_ia)
            st.markdown(texto_exibicao) # Usando markdown para ficar bonito
            
            # Campo de cópia rápida
            st.divider()
            st.subheader("📋 Copiar Textos")
            st.text_area("Copie aqui título, descrição e tags:", texto_exibicao, height=300)
        
        with col2:
            # Extrair Capa
            match = re.search(r'CAPA:\s*(\d+)', texto_ia)
            segundo = int(match.group(1)) if match else 1
            
            cap = cv2.VideoCapture(video_path)
            cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
            success, frame = cap.read()
            
            if success:
                st.subheader(f"🖼️ Thumbnail Sugerida (Seg {segundo})")
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                st.image(frame_rgb, use_container_width=True)
                
                # Botão de download da capa
                ret, buffer = cv2.imencode('.jpg', frame)
                st.download_button(label="📥 Baixar Capa", data=buffer.tobytes(), file_name="capa_sugerida.jpg", mime="image/jpeg")
            
            cap.release()
            
            st.success("Análise Finalizada!")
            st.balloons()
        
        # Limpeza na Google API
        genai.delete_file(video_file.name)
        
    except Exception as e:
        st.error(f"Erro na análise: {e}")
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
