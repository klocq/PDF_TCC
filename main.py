from extrator import extrair_texto_pdf
from processador import processar_texto_bruto
from transformador_pandas import aplicar_transformacoes_pandas, exportar_relatorios_finais

def rodar_pipeline():
    # 1. Definição dos arquivos de entrada e saída
    arquivo_pdf_20261 = "CADASTRO_TURMAS_20261.pdf"
    arquivo_pdf_20262 = "CADASTRO_TURMAS_20262.pdf"
    
    arquivo_excel_saida_20261 = "Grade_Horarios_UFSC_20261.xlsx"
    arquivo_excel_saida_20262 = "Grade_Horarios_UFSC_20262.xlsx"
    
    print("=" * 60)
    print("INICIANDO PIPELINE AUTOMATIZADO (PDF -> PANDAS -> EXCEL)")
    print("=" * 60)
    
    # -------------------------------------------------------------
    # PROCESSAMENTO DO SEMESTRE 20261
    # -------------------------------------------------------------
    print("\n>>> [PASSO 1/2] Processando Semestre 20261...")
    
    # Extração e Limpeza Textual Bruta
    texto_bruto_20261 = extrair_texto_pdf(arquivo_pdf_20261)
    dados_estruturados_20261 = processar_texto_bruto(texto_bruto_20261)
    
    # Transformação Inteligente com Pandas e Geração das Grades
    if dados_estruturados_20261:
        df_enriquecido_20261 = aplicar_transformacoes_pandas(dados_estruturados_20261)
        exportar_relatorios_finais(df_enriquecido_20261, arquivo_excel_saida_20261)
    else:
        print("[ALERTA] Nenhuma turma encontrada para o semestre 20261.")

    # -------------------------------------------------------------
    # PROCESSAMENTO DO SEMESTRE 20262
    # -------------------------------------------------------------
    print("\n>>> [PASSO 2/2] Processando Semestre 20262...")
    
    # Extração e Limpeza Textual Bruta
    texto_bruto_20262 = extrair_texto_pdf(arquivo_pdf_20262)
    dados_estruturados_20262 = processar_texto_bruto(texto_bruto_20262)
    
    # Transformação Inteligente com Pandas e Geração das Grades
    if dados_estruturados_20262:
        df_enriquecido_20262 = aplicar_transformacoes_pandas(dados_estruturados_20262)
        exportar_relatorios_finais(df_enriquecido_20262, arquivo_excel_saida_20262)
    else:
        print("[ALERTA] Nenhuma turma encontrada para o semestre 20262.")

    print("\n" + "=" * 60)
    print("PIPELINE EXECUTADO COM SUCESSO! PLANILHAS MODULARES GERADAS.")
    print("=" * 60)


if __name__ == "__main__":
    rodar_pipeline()