import sys
import os
import io

# Adiciona a pasta 'funcoes' ao caminho do Python
PASTA_FUNCOES = os.path.abspath(os.path.join(os.path.dirname(__file__), "funcoes"))
if PASTA_FUNCOES not in sys.path:
    sys.path.append(PASTA_FUNCOES)

import streamlit as st
import pandas as pd

from banco import supabase
from main import processar_pdf_individual
from transformador_pandas import gerar_grade_horaria_fase, exportar_relatorios_finais

# Configuração da página no Streamlit
st.set_page_config(
    page_title="Gestão de Turmas - CI/UFSC",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Sistema de Gestão Curricular e Turmas - CI / UFSC")

# Criação das Abas Principais
aba_upload, aba_consulta = st.tabs(["📤 Envio de Arquivos (ETL)", "🔍 Consulta e Grade Horária"])

# ==========================================
# ABA 1: UPLOAD E PROCESSAMENTO DE PDF
# ==========================================
with aba_upload:
    st.header("Upload do Cadastro de Turmas (PDF)")
    st.write("Envie o arquivo PDF de oferta de turmas para processar e atualizar o banco de dados e relatórios.")
    
    pdf_enviado = st.file_uploader("Selecione o arquivo PDF das turmas", type=["pdf"])
    
    if pdf_enviado is not None:
        if st.button("🚀 Processar e Salvar no Supabase", use_container_width=True):
            with st.spinner("Processando pipeline de dados..."):
                dir_entradas = os.path.abspath(os.path.join(os.path.dirname(__file__), "entradas"))
                dir_resultados = os.path.abspath(os.path.join(os.path.dirname(__file__), "resultados"))
                
                os.makedirs(dir_entradas, exist_ok=True)
                os.makedirs(dir_resultados, exist_ok=True)

                caminho_temp = os.path.join(dir_entradas, pdf_enviado.name)
                caminho_excel = os.path.join(dir_resultados, "relatorio_final.xlsx")

                with open(caminho_temp, "wb") as f:
                    f.write(pdf_enviado.getbuffer())
                
                sucesso, msg = processar_pdf_individual(caminho_temp, caminho_excel)
                
                if sucesso:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(msg)

# ==========================================
# ABA 2: CONSULTA E GRADE HORÁRIA VISUAL
# ==========================================
with aba_consulta:
    st.header("Consulta de Turmas e Grade Semanal")

    @st.cache_data(ttl=10)
    def carregar_dados_banco():
        try:
            res = supabase.table("turmas_ci").select("*").execute()
            return pd.DataFrame(res.data)
        except Exception as e:
            st.error(f"Erro ao carregar dados do Supabase: {e}")
            return pd.DataFrame()

    df_turmas = carregar_dados_banco()

    if df_turmas.empty:
        st.info("Nenhuma turma encontrada no banco de dados. Envie um arquivo PDF na aba anterior para carregar os dados.")
    else:
        # Padronização e renomeação de colunas vindas do banco
        colunas_map = {
            "codigo_disciplina": "Código da Disciplina",
            "turma": "Turma",
            "nome_disciplina": "Nome da Disciplina",
            "fase": "Fase",
            "tipo": "Tipo",
            "tipo_disciplina": "Núcleo",
            "horas_aula": "Horas Aula",
            "ofertas": "Ofertas",
            "horario": "Horário",
            "local": "Local",
            "professor": "Professor",
            "semestre": "Semestre"
        }
        df_turmas.rename(columns=colunas_map, inplace=True)

        # Remove eventuais duplicatas de nome de colunas
        df_turmas = df_turmas.loc[:, ~df_turmas.columns.duplicated()]

        # ------------------------------------------
        # BOTÃO DE DOWNLOAD DO EXCEL COMPLETO (MULTI-ABAS)
        # ------------------------------------------
        st.subheader("📦 Exportação Completa")
        
        buffer_excel = io.BytesIO()
        df_exportar = df_turmas.copy()
        
        # Chama a função de exportação para gerar as abas formatadas
        exportar_relatorios_finais(df_exportar, buffer_excel)
        
        st.download_button(
            label="📊 Baixar Planilha Completa em Excel (Todas as Fases e Grids)",
            data=buffer_excel.getvalue(),
            file_name="relatorio_turmas_completo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        st.markdown("---")

        # ------------------------------------------
        # FILTROS SIMPLIFICADOS (FASE E PROFESSOR)
        # ------------------------------------------
        st.subheader("🛠️ Filtros de Pesquisa")
        c1, c2 = st.columns(2)

        opcoes_fases = ["Todas", "1ª Fase", "2ª Fase", "3ª Fase", "4ª Fase", "5ª Fase", "6ª Fase", "Optativas / Outras"]

        with c1:
            filtro_fase = st.selectbox("Fase", opcoes_fases)

        with c2:
            profs = ["Todos"] + sorted(list(df_turmas["Professor"].dropna().unique()))
            filtro_prof = st.selectbox("Professor", profs)

        # Aplicação dos Filtros
        df_filtrado = df_turmas.copy()

        if filtro_fase != "Todas":
            if filtro_fase == "5ª Fase":
                df_filtrado = df_filtrado[df_filtrado["Fase"].astype(str).str.contains("5ª Fase", na=False)]
            elif filtro_fase == "6ª Fase":
                df_filtrado = df_filtrado[df_filtrado["Fase"].astype(str).str.contains("6ª Fase", na=False)]
            elif filtro_fase == "Optativas / Outras":
                df_filtrado = df_filtrado[df_filtrado["Fase"].astype(str).str.contains("Optativa|Outros", case=False, na=False)]
            else:
                df_filtrado = df_filtrado[df_filtrado["Fase"] == filtro_fase]

        if filtro_prof != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Professor"] == filtro_prof]

        # ------------------------------------------
        # VISUALIZAÇÃO DA GRADE HORÁRIA SEMANAL
        # ------------------------------------------
        st.subheader("🗓️ Matriz de Grade Horária Semanal")

        if not df_filtrado.empty:
            grade_semanal = gerar_grade_horaria_fase(df_filtrado)
            st.dataframe(grade_semanal, use_container_width=True, height=400)
        else:
            st.warning("Nenhuma turma encontrada para a combinação de filtros selecionada.")

        # ------------------------------------------
        # TABELA DETALHADA E DOWNLOAD FILTRADO
        # ------------------------------------------
        st.markdown("---")
        st.subheader("📋 Lista Detalhada das Turmas Selecionadas")
        
        colunas_exibicao = ["Código da Disciplina", "Turma", "Nome da Disciplina", "Fase", "Tipo", "Núcleo", "Horário", "Local", "Professor", "Semestre"]
        colunas_existentes = [c for c in colunas_exibicao if c in df_filtrado.columns]
        
        df_exibicao = df_filtrado[colunas_existentes].copy()
        df_exibicao = df_exibicao.loc[:, ~df_exibicao.columns.duplicated()]

        # Download apenas da seleção filtrada
        buffer_filtrado = io.BytesIO()
        with pd.ExcelWriter(buffer_filtrado, engine="openpyxl") as writer:
            df_exibicao.to_excel(writer, index=False, sheet_name="Selecao_Filtrada")

        st.download_button(
            label="📥 Baixar Apenas Tabela Filtrada (.xlsx)",
            data=buffer_filtrado.getvalue(),
            file_name="turmas_filtradas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.dataframe(
            df_exibicao,
            use_container_width=True,
            hide_index=True
        )