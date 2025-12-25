import streamlit as st
import google.generativeai as genai
import cv2
import os
import re
import tempfile
import time

# Configuração da Página
st.set_page_config(page_title="BrendaBot Viral Ultra", page_icon="🔥", layout="wide")
st.title("🔥 Validador de Viabilidade e Viralização")

# Configurar API
API_KEY = "AIzaSyAXMHYg7kRRA74fwOXxH9mP3hqF4H2h2sg"
genai.configure(api_key=API_KEY)

# Mantendo o modelo que você usa
model = genai.GenerativeModel('models/gemini-2.5-flash')

uploaded_file = st.file_uploader("Suba o vídeo para validação estratégica...", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') 
    tfile.write(uploaded_file.read())
    video_path = tfile.name
    
    st.info("🕵️ Analisando riscos e potencial... Aguarde.")
    
    try:
        video_file = genai.upload_file(path=video_path, mime_type="video/mp4")
        
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
            
        # PROMPT FOCADO EM VIABILIDADE E DIRETRIZES PRIMEIRO
        prompt = """
        Atue como Especialista em Algoritmo do YouTube e Moderador de Conteúdo. 
        Analise o vídeo e retorne o relatório RIGOROSAMENTE nesta ordem:

        ### 🚨 PAINEL DE VIABILIDADE (LEIA PRIMEIRO)
        1. **RISCO DE RESTRIÇÃO**: (O vídeo viola diretrizes? Tem palavras proibidas, temas sensíveis ou algo que possa causar "Shadowban" ou desmonetização? Dê um status: SEGURO, ARRISCADO ou CRÍTICO).
        2. **CHANCE DE FEED**: (O algoritmo vai distribuir este vídeo no Shorts/Feed? Analise se o conteúdo é original e visualmente atraente para a plataforma).
        3. **VEREDITO DO GANCHO (HOOK)**: (O início prende em 3 segundos? Se não, o vídeo vai 'morrer' cedo. Nota 0-10).

        ### 📈 ANÁLISE DE PERFORMANCE
        4. **POTENCIAL DE VIRALIZAÇÃO**: (0 a 100% e justificativa).
        5. **PONTOS DE ABANDONO**: (Em quais segundos o vídeo fica chato e o público vai sair?).

        ### 📝 ATIVOS DE POSTAGEM (Caso decida postar)
        6. **TÍTULO E HASHTAGS**.
        7. **DESCRIÇÃO SEO**.
        8. **CAPÍTULOS E CORTES**.
        9. **COMENTÁRIO FIXADO**.
        10. **QUOTES PARA REDES SOCIAIS**.

        ### 🌍 TRADUÇÃO
        11. Título e Descrição em Inglês.

        ### 🖼️ THUMBNAIL
        Escreva ao final apenas: 'CAPA: X' (onde X é o melhor segundo).
        """
        
        response = model.generate_content([video_file, prompt])
        texto_ia = response.text
        
        col1, col2 = st.columns([1.2, 0.8])
        
        with col1:
            st.subheader("📋 Relatório Estratégico")
            # Exibe o texto completo (que agora começa com os riscos)
            texto_exibicao = re.sub(r'CAPA:\s*\d+', '', texto_ia)
            st.markdown(texto_exibicao)
        
        with col2:
            match = re.search(r'CAPA:\s*(\d+)', texto_ia)
            segundo = int(match.group(1)) if match else 1
            
            cap = cv2.VideoCapture(video_path)
            cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
            success, frame = cap.read()
            
            if success:
                st.subheader(f"🖼️ Sugestão de Capa (Seg {segundo})")
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                st.image(frame_rgb, use_container_width=True)
                
                ret, buffer = cv2.imencode('.jpg', frame)
                st.download_button(label="📥 Baixar Capa", data=buffer.tobytes(), file_name="thumbnail.jpg", mime="image/jpeg")
            
            cap.release()
            
            # Alerta visual baseado no texto
            if "CRÍTICO" in texto_ia or "ARRISCADO" in texto_ia:
                st.warning("⚠️ Atenção: Este vídeo possui riscos de performance ou diretrizes.")
            else:
                st.success("✅ Vídeo validado para postagem!")
        
        genai.delete_file(video_file.name)
        
    except Exception as e:
        st.error(f"Erro: {e}")
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
