'''from extrator import extrair_texto_pdf
from processador import processar_texto_bruto
from escritor import salvar_em_csv

def rodar_pipeline():
    arquivo_pdf = "CADASTRO_TURMAS_20262.pdf"
    arquivo_csv_saida = "resultado_turmas.csv"
    
    # 1. Extração do Texto Bruto
    texto_bruto = extrair_texto_pdf(arquivo_pdf)
    
    # 2. Processamento e Limpeza
    dados_finais = processar_texto_bruto(texto_bruto)
    
    # 3. Exportação para Planilha CSV
    salvar_em_csv(dados_finais, arquivo_csv_saida)

if __name__ == "__main__":
    rodar_pipeline()'''

'''from extrator import extrair_texto_pdf

def investigar_dado_bruto():
    arquivo_pdf = "CADASTRO_TURMAS_20262.pdf"
    
    # 1. Extrai o texto puro
    texto_bruto = extrair_texto_pdf(arquivo_pdf)
    
    # 2. Em vez de printar e sumir no terminal, vamos salvar em um arquivo .txt
    print("Salvando o texto bruto para análise visual...")
    with open("texto_bruto.txt", "w", encoding="utf-8") as f:
        f.write(texto_bruto)
        
    print("\n--- PRONTO! ---")
    print("Abra o arquivo 'texto_bruto.txt' que apareceu na barra lateral do VS Code.")
    print("Copie e cole aqui os primeiros 3 ou 4 blocos de turmas exatamente como aparecem lá.")

if __name__ == "__main__":
    investigar_dado_bruto()'''

from extrator import extrair_texto_pdf
from processador import processar_texto_bruto
from escritor import salvar_em_csv

def rodar_pipeline():
    arquivo_pdf = "CADASTRO_TURMAS_20261.pdf"
    arquivo_pdf2 = "CADASTRO_TURMAS_20262.pdf"
    arquivo_csv_saida = "resultado_turmas.csv"
    arquivo_csv_saida2 = "resultado_turmas2.csv"
    
    # 1. Extração do Texto
    texto_bruto = extrair_texto_pdf(arquivo_pdf)
    texto_bruto2 = extrair_texto_pdf(arquivo_pdf2)
    print(texto_bruto)
    print(texto_bruto2)
    # 2. Processamento Inteligente
    dados_finais = processar_texto_bruto(texto_bruto)
    dados_finais2 = processar_texto_bruto(texto_bruto2)
    # 3. Escrita na Planilha
    salvar_em_csv(dados_finais, arquivo_csv_saida)
    salvar_em_csv(dados_finais2, arquivo_csv_saida2)
    print("Pipeline executado com sucesso! Arquivo gerado.")


if __name__ == "__main__":
    rodar_pipeline()