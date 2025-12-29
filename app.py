"""
Viral Strategist Pro - Versão DEBUG
Identifica problemas com a API Key
"""

import streamlit as st
import google.generativeai as genai

# ============================================
# 🔑 COLE SUA API KEY DO GEMINI ABAIXO
# ============================================
GEMINI_API_KEY = "AIzaSyD8ijELhs2zJKFksT6w6qidZ21aLGGdcC0"
# ============================================

st.set_page_config(
    page_title="Viral Strategist Pro - DEBUG",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="expanded"
)

def testar_api_key(api_key):
    """Testa a API Key e mostra os modelos disponíveis"""
    try:
        genai.configure(api_key=api_key)
        modelos = genai.list_models()
        return modelos
    except Exception as e:
        return None

def main():
    st.title("🚀 Viral Strategist Pro")
    st.markdown("**🔍 Versão DEBUG - Diagnóstico da API**")
    st.divider()
    
    api_key_configurada = GEMINI_API_KEY and GEMINI_API_KEY != "cole_sua_api_key_aqui"
    
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        if api_key_configurada:
            st.success("✅ API Key inserida!")
            st.code(GEMINI_API_KEY[:10] + "...")
        else:
            st.error("⚠️ API Key não configurada!")
    
    if not api_key_configurada:
        st.error("⚠️ API Key não configurada!")
        st.info("Cole sua API Key no GitHub (linha 15)")
        st.stop()
    
    # Teste da API Key
    st.subheader("🔍 Testando API Key...")
    
    with st.spinner("Conectando ao Google Gemini..."):
        modelos = testar_api_key(GEMINI_API_KEY)
    
    if modelos is None:
        st.error("❌ ERRO na API Key!")
        
        st.markdown("""
        ### ❌ Problema Identificado:
        
        Sua API Key não funcionou.
        
        ### ✅ Solução:
        
        1. Acesse: https://aistudio.google.com/app/apikey
        2. Clique no seu nome (canto superior direito)
        3. Selecione "Manage API Keys"
        4. Delete chaves antigas e crie uma NOVA
        5. Selecione "Create API key in new project"
        6. Copie a nova chave
        7. Atualize no GitHub
        8. Redeploy
        """)
        
    else:
        st.success("✅ API Key funcionando!")
        
        st.subheader("📋 Modelos Disponíveis:")
        for m in modelos:
            st.write(f"- {m.name}")
        
        st.info("Se gemini-1.5-pro ou gemini-1.5-flash não apareceram, "
                "crie uma nova API Key no Google AI Studio!")

if __name__ == "__main__":
    main()
