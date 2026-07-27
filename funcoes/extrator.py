from pypdf import PdfReader

# ____________________________________________________
# 1 - O que faz?
# ----------------------------------------------------
# Extrai o texto contido em todas as páginas de um PDF
# e o concatena em uma única string.
# ____________________________________________________
def extrair_texto_pdf(caminho_do_pdf):
    leitor = PdfReader(caminho_do_pdf)
    texto_completo = ""
    
    for pagina in leitor.pages:
        texto_da_pagina = pagina.extract_text()
        if texto_da_pagina:
            texto_completo += texto_da_pagina + "\n"
            
    return texto_completo