from extrator import extrair_texto_pdf
from processador import processar_texto_bruto
from tratamento_dados import aplicar_tratamento_completo
from transformador_pandas import exportar_relatorios_finais
from banco import salvar_turmas_no_banco


def rodar_pipeline():
    # Caminhos dos arquivos
    arquivo_pdf_20261 = r"C:\Users\cadum\Desktop\Projeto_TCC\PDF_TCC\arquivos_entrada\CADASTRO_TURMAS_20261.pdf"
    arquivo_pdf_20262 = r"C:\Users\cadum\Desktop\Projeto_TCC\PDF_TCC\arquivos_entrada\CADASTRO_TURMAS_20262.pdf"

    arquivo_excel_20261 = r"C:\Users\cadum\Desktop\Projeto_TCC\PDF_TCC\resultados\Grade_Horarios_UFSC_20261.xlsx"
    arquivo_excel_20262 = r"C:\Users\cadum\Desktop\Projeto_TCC\PDF_TCC\resultados\Grade_Horarios_UFSC_20262.xlsx"

    lista_processamento = [
        (arquivo_pdf_20261, arquivo_excel_20261),
        (arquivo_pdf_20262, arquivo_excel_20262)
    ]

    print("=" * 60)
    print("INICIANDO PIPELINE (PDF -> TRATAMENTO -> EXCEL -> SUPABASE)")
    print("=" * 60)

    for pdf_input, excel_output in lista_processamento:
        texto_bruto = extrair_texto_pdf(pdf_input)
        dados_brutos = processar_texto_bruto(texto_bruto)

        if dados_brutos:
            # Novo modulo de tratamento centralizado
            df_tratado = aplicar_tratamento_completo(dados_brutos, caminho_pdf=pdf_input)
            
            # Geracao de relatorios e envio ao banco
            exportar_relatorios_finais(df_tratado, excel_output)
            salvar_turmas_no_banco(df_tratado)

    print("\n" + "=" * 60)
    print("PIPELINE EXECUTADO COM SUCESSO!")
    print("=" * 60)


if __name__ == "__main__":
    rodar_pipeline()