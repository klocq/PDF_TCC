# pipeline.py (ou main.py)
import os
from extrator import extrair_texto_pdf
from processador import processar_texto_bruto
from tratamento_dados import aplicar_tratamento_completo
from transformador_pandas import exportar_relatorios_finais
from banco import salvar_turmas_no_banco


def processar_pdf_individual(caminho_pdf_entrada: str, caminho_excel_saida: str):
    """
    Executa o pipeline completo para um unico arquivo PDF enviado.
    """
    print(f"\n>>> Processando arquivo: {caminho_pdf_entrada}")

    # 1. Extração e Limpeza Textual
    texto_bruto = extrair_texto_pdf(caminho_pdf_entrada)
    dados_brutos = processar_texto_bruto(texto_bruto)

    if not dados_brutos:
        return False, "Nenhuma turma encontrada no arquivo PDF fornecido."

    # 2. Tratamento Inteligente com Pandas (Separação de colunas e Semestre)
    df_tratado = aplicar_tratamento_completo(dados_brutos, caminho_pdf=caminho_pdf_entrada)

    # 3. Exportação para Excel (.xlsx)
    exportar_relatorios_finais(df_tratado, caminho_excel_saida)

    # 4. Ingestão na Nuvem (Supabase)
    salvar_turmas_no_banco(df_tratado)

    semestre_detectado = df_tratado["Semestre"].iloc[0]
    total_turmas = len(df_tratado)

    return True, f"Sucesso! {total_turmas} turmas do semestre {semestre_detectado} foram processadas e enviadas ao banco."