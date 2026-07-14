from pypdf import PdfReader

def extrair_texto_pdf(caminho_do_pdf):
    """
    Abre um arquivo PDF e extrai todo o texto contido nele.
    Retorna uma string única com o texto completo de todas as páginas.
    """
    print(f"Iniciando a extração do arquivo: {caminho_do_pdf}")
    
    # 1. Carrega o arquivo PDF na memória
    leitor = PdfReader(caminho_do_pdf)
    texto_completo = ""
    
    # 2. Percorre cada página do PDF extraindo o texto e juntando tudo
    for numero_pagina, pagina in enumerate(leitor.pages):
        texto_da_pagina = pagina.extract_text()
        if texto_da_pagina:
            texto_completo += texto_da_pagina + "\n"
            
    print("Extração do PDF concluída com sucesso!")
    return texto_completo