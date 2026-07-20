import os
import sys

# -------------------------------------------
# Adiciona a pasta 'funcoes' ao caminho de busca do Python
# -------------------------------------------
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
pasta_funcoes = os.path.join(diretorio_atual, "funcoes")

if pasta_funcoes not in sys.path:
    sys.path.insert(0, pasta_funcoes)

import streamlit as st
# Agora você pode importar 'main' diretamente, e o 'main' vai achar os outros módulos!
from main import processar_pdf_individual

# Configuration da página do Streamlit
st.set_page_config(
    page_title="Sistema de Horários UFSC",
    page_icon="📚",
    layout="centered"
)

st.title("📚 Processador de Cadastro de Turmas UFSC")
st.markdown("Faça o upload do relatório em PDF para extrair, tratar e salvar os dados no **Supabase** e gerar a planilha Excel.")

st.divider()

# -------------------------------------------
# Componente de Upload de Arquivo (PDF)
# -------------------------------------------
arquivo_pdf_enviado = st.file_uploader(
    label="Selecione ou arraste o arquivo PDF (ex: CADASTRO_TURMAS_20261.pdf)",
    type=["pdf"],
    accept_multiple_files=False
)

if arquivo_pdf_enviado is not None:
    # Exibe informações do arquivo selecionado
    st.info(f"📄 Arquivo selecionado: **{arquivo_pdf_enviado.name}** ({arquivo_pdf_enviado.size / 1024:.1f} KB)")

    # Botão para disparar o pipeline
    if st.button("🚀 Processar e Enviar para o Banco", type="primary"):
        with st.spinner("Processando PDF, aplicando regras do Pandas e enviando para a nuvem..."):
            try:
                # -------------------------------------------
                # 1. Salvando o arquivo PDF na pasta local
                # -------------------------------------------
                pasta_entrada = os.path.join(os.getcwd(), "arquivos_entrada")
                pasta_saida = os.path.join(os.getcwd(), "resultados")
                
                os.makedirs(pasta_entrada, exist_ok=True)
                os.makedirs(pasta_saida, exist_ok=True)

                caminho_pdf_local = os.path.join(pasta_entrada, arquivo_pdf_enviado.name)
                
                # Gravando o buffer recebido da Web no disco rígido local
                with open(caminho_pdf_local, "wb") as f:
                    f.write(arquivo_pdf_enviado.getbuffer())

                # Definindo o nome da planilha de saída correspondente
                nome_base = os.path.splitext(arquivo_pdf_enviado.name)[0]
                caminho_excel_local = os.path.join(pasta_saida, f"Grade_Horarios_{nome_base}.xlsx")

                # -------------------------------------------
                # 2. Chamando o Backend do Python
                # -------------------------------------------
                sucesso, mensagem = processar_pdf_individual(caminho_pdf_local, caminho_excel_local)

                if sucesso:
                    st.success(mensagem)
                    st.balloons()

                    # Disponibiliza o download da planilha Excel gerada direto na tela
                    with open(caminho_excel_local, "rb") as file_excel:
                        st.download_button(
                            label="📥 Baixar Planilha Excel Gerada",
                            data=file_excel,
                            file_name=os.path.basename(caminho_excel_local),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.warning(mensagem)

            except Exception as e:
                st.error(f"❌ Ocorreu um erro ao processar o arquivo: {e}")