import os
import sys

# Garante que o diretório 'funcoes' seja reconhecido pelo Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extrator import extrair_texto_pdf
from processador import processar_texto_bruto
from tratamento_dados import aplicar_tratamento_completo
from transformador_pandas import exportar_relatorios_finais
from banco import salvar_turmas_no_banco, supabase


def processar_pdf_individual(caminho_pdf_entrada: str, caminho_excel_saida: str, curriculo: str = "20161"):
    """
    Executa o pipeline completo para um único arquivo PDF enviado,
    considerando o currículo selecionado ('20161' ou '20261').
    """
    print(f"\n>>> Processando arquivo: {caminho_pdf_entrada} | Currículo: {curriculo}")

    # 1. Extração e Limpeza Textual
    texto_bruto = extrair_texto_pdf(caminho_pdf_entrada)
    dados_brutos = processar_texto_bruto(texto_bruto)

    if not dados_brutos:
        return False, "Nenhuma turma encontrada no arquivo PDF fornecido."

    # 2. Tratamento Inteligente com Pandas (enriquecimento via Supabase e currículo escolhido)
    df_tratado = aplicar_tratamento_completo(
        dados_brutos, 
        caminho_pdf=caminho_pdf_entrada, 
        supabase_client=supabase,
        curriculo=curriculo
    )

    # 3. Exportação para Excel (.xlsx)
    exportar_relatorios_finais(df_tratado, caminho_excel_saida)

    # 4. Salvar turmas tratadas no Banco
    salvar_turmas_no_banco(df_tratado)

    return True, df_tratado