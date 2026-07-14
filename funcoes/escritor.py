import csv

def salvar_em_csv(dados, caminho_saida):
    """
    Recebe a lista de dicionários com as turmas e exporta para um arquivo CSV 
    usando ponto e vírgula (;) como separador para abrir direto no Excel em português.
    """
    if not dados:
        print("Nenhum dado encontrado para salvar.")
        return

    print(f"Salvando dados no arquivo: {caminho_saida}...")
    
    # Coleta os nomes das colunas com base nas chaves do primeiro dicionário
    colunas = dados[0].keys()
    
    # encoding='utf-8-sig' adiciona o sinalizador BOM que força o Excel a reconhecer os acentos
    with open(caminho_saida, mode='w', newline='', encoding='utf-8-sig') as arquivo:
        # Mudamos o delimiter para ';' para o Excel quebrar em colunas automaticamente
        escritor = csv.DictWriter(arquivo, fieldnames=colunas, delimiter=';')
        
        # Escreve o cabeçalho das colunas
        escritor.writeheader()
        
        # Escreve todas as linhas de turmas
        escritor.writerows(dados)
        
    print("Arquivo CSV gerado com sucesso!")