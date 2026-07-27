import sys
import os

# 1. Registra a pasta 'funcoes' no caminho do Python PRIMEIRO
PASTA_FUNCOES = os.path.abspath(os.path.join(os.path.dirname(__file__), "funcoes"))
if PASTA_FUNCOES not in sys.path:
    sys.path.append(PASTA_FUNCOES)

# 2. Agora pode fazer as importações normalmente
import streamlit as st
import pandas as pd
import io

from banco import supabase
from main import processar_pdf_individual
from transformador_pandas import gerar_grade_horaria_fase, exportar_relatorios_finais
from auditoria_conflitos import detectar_todos_conflitos  # <-- Importação aqui depois do sys.path
from data_quality import executar_auditoria_data_quality

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
    st.write("Envie o arquivo PDF de oferta de turmas para processar, sanitizar e atualizar o banco de dados e relatórios.")
    
    pdf_enviado = st.file_uploader("Selecione o arquivo PDF das turmas", type=["pdf"])
    
    if pdf_enviado is not None:
        if st.button("🚀 Processar e Salvar no Supabase", use_container_width=True):
            with st.spinner("Processando pipeline de dados (ETL)..."):
                # Garante diretórios absolutos e limpos
                dir_entradas = os.path.abspath(os.path.join(os.path.dirname(__file__), "entradas"))
                dir_resultados = os.path.abspath(os.path.join(os.path.dirname(__file__), "resultados"))
                
                os.makedirs(dir_entradas, exist_ok=True)
                os.makedirs(dir_resultados, exist_ok=True)

                # Salva o arquivo temporário enviado pelo usuário
                caminho_pdf_entrada = os.path.join(dir_entradas, pdf_enviado.name)
                caminho_excel_saida = os.path.join(dir_resultados, "relatorio_final.xlsx")

                with open(caminho_pdf_entrada, "wb") as f:
                    f.write(pdf_enviado.getbuffer())
                
                # Executa o pipeline apenas com o arquivo fornecido pelo usuário
                sucesso, msg = processar_pdf_individual(caminho_pdf_entrada, caminho_excel_saida)
                
                if sucesso:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(msg)
    else:
        st.info("📌 Aguardando envio do arquivo PDF para iniciar o processamento.")

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
        # ------------------------------------------
        # PAINEL DE AUDITORIA E DETECÇÃO DE CONFLITOS
        # ------------------------------------------
        st.markdown("---")
        st.subheader("🚨 Auditoria Pedagógica e Detecção de Conflitos")

        conf_prof, conf_sala, conf_fase = detectar_todos_conflitos(df_filtrado)
        total_conflitos = len(conf_prof) + len(conf_sala) + len(conf_fase)

        if total_conflitos == 0:
            st.success("✅ Nenhum conflito de horário, professor ou sala detectado na seleção atual!")
        else:
            st.warning(f"⚠️ Foram encontrados **{total_conflitos} conflitos/alertas** na seleção atual.")
            
            exp1, exp2, exp3 = st.columns(3)
            
            with exp1:
                st.metric("Choques de Professor", len(conf_prof))
            with exp2:
                st.metric("Choques de Sala/Local", len(conf_sala))
            with exp3:
                st.metric("Sobreposições de Fase", len(conf_fase))

            with st.expander("🔍 Ver Detalhes dos Conflitos Detectados", expanded=True):
                tab_p, tab_s, tab_f = st.tabs(["👨‍🏫 Conflitos de Professor", "🏫 Conflitos de Sala", "📚 Sobreposição de Fase"])
                
                with tab_p:
                    if conf_prof:
                        for c in conf_prof:
                            st.error(f"**{c['dia']} às {c['hora']}**: {c['detalhe']}")
                    else:
                        st.info("Nenhum choque de professor encontrado.")

                with tab_s:
                    if conf_sala:
                        for c in conf_sala:
                            st.error(f"**{c['dia']} às {c['hora']}**: {c['detalhe']}")
                    else:
                        st.info("Nenhum choque de sala/local encontrado.")

                with tab_f:
                    if conf_fase:
                        for c in conf_fase:
                            st.warning(f"**{c['fase']} - {c['dia']} às {c['hora']}**: {c['detalhe']}")
                    else:
                        st.info("Nenhuma sobreposição de horário na mesma fase encontrada.")


        # ------------------------------------------
        # RELATÓRIO DE DATA QUALITY
        # ------------------------------------------
        st.subheader("🛡️ Relatório de Data Quality & Sanitização")
        
        relatorio_dq = executar_auditoria_data_quality(df_turmas)
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Total de Turmas", relatorio_dq["total_registros"])
        col_m2.metric("Horários Válidos", f"{relatorio_dq['metricas']['pct_horarios_validos']}%")
        col_m3.metric("Professores Alocados", f"{relatorio_dq['metricas']['pct_professores_definidos']}%")
        col_m4.metric("Salas Reservadas", f"{relatorio_dq['metricas']['pct_salas_definidas']}%")

        if relatorio_dq["alertas"]:
            with st.expander("⚠️ Ver Avisos de Integridade de Dados", expanded=False):
                for alerta in relatorio_dq["alertas"]:
                    st.write(alerta)
        else:
            st.success("✅ " + relatorio_dq["mensagem"])

        st.markdown("---")