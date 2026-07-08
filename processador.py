import re

def processar_texto_bruto(texto_bruto):
    """
    Versão restaurada: Varre o texto linha por linha (localizando as 25 turmas),
    e limpa os campos de forma direta.
    """
    print("Reestabelecendo o processamento linha por linha...")
    dados_estruturados = []
    
    # Quebra o texto exatamente nas linhas reais
    linhas = texto_bruto.split("\n")
    
    # Padrão estável para achar o Código e a Turma (Ex: CAD5103 01342C)
    padrao_codigo_turma = re.compile(r'([A-Z]{3}\d{4})\s+(\d{5}[A-Z]?)')

    for i, linha in enumerate(linhas):
        linha = linha.strip().replace('"', '')
        
        # Ignora cabeçalhos limpos
        if not linha or "Semestre:" in linha or "CADASTRO DE TURMAS" in linha:
            continue
            
        match = padrao_codigo_turma.search(linha)
        
        if match:
            codigo = match.group(1)
            turma = match.group(2)
            
            # --- 1. CAPTURA DO NOME DA DISCIPLINA ---
            # Pegamos o texto da linha e removemos o código e a turma dela
            nome_disciplina = linha.replace(codigo, "").replace(turma, "").strip()
            
            # Se o nome veio com números grudados no final (ex: "Administração I 72 12"),
            # removemos esses números finais usando Regex para o nome ficar limpo
            nome_disciplina = re.sub(r'\s+\d+.*$', '', nome_disciplina).strip()
            
            # Se o nome ficou vazio, tentamos resgatar da linha anterior
            if not nome_disciplina and i > 0:
                nome_disciplina = linhas[i-1].replace('"', '').strip()

            # --- 2. CAPTURA DAS HORAS AULA E OFERTAS ---
            horas_aula = "N/A"
            ofertas = "N/A"
            contexto_numerico = []
            
            # Olhamos as linhas de baixo para catar os números soltos de H.A. e Vagas
            for j in range(1, 6):
                if i + j < len(linhas):
                    val = linhas[i+j].replace('"', '').strip()
                    if val.isdigit():
                        contexto_numerico.append(val)
            
            if len(contexto_numerico) >= 2:
                horas_aula = contexto_numerico[0]
                ofertas = contexto_numerico[1]

            # --- 3. HORÁRIO E PROFESSOR ---
            horario_local = "A definir"
            professor = "A contratar"
            padrao_horario = r'(\d\.\d{4}-\d/[A-Z0-9-]+)'
            
            # Vasculha as linhas abaixo para achar o código de horário da UFSC
            for j in range(1, 10):
                if i + j < len(linhas):
                    linha_analise = linhas[i+j].replace('"', '').strip()
                    match_horario = re.search(padrao_horario, linha_analise)
                    
                    if match_horario:
                        horario_local = match_h_local = match_horario.group(1)
                        
                        # O que sobrar na linha do horário geralmente é o professor
                        possivel_prof = linha_analise.replace(horario_local, "").strip()
                        if possivel_prof and not possivel_prof.isdigit():
                            professor = possivel_prof
                        elif i + j - 1 >= 0:
                            # Se não, espia a linha logo acima do horário
                            linha_cima = linhas[i+j-1].replace('"', '').strip()
                            if len(linha_cima) > 3 and not linha_cima.isdigit() and codigo not in linha_cima:
                                professor = linha_cima
                        break

            # Evita cabeçalhos fantasmas
            if "Disciplina" in nome_disciplina or "Nome da" in nome_disciplina:
                continue

            registro = {
                "Código da Disciplina": codigo,
                "Turma": turma,
                "Nome da Disciplina": nome_disciplina if nome_disciplina else "Grade Horária",
                "Horas Aula": horas_aula,
                "Ofertas": ofertas,
                "Horário/Local": horario_local,
                "Professor": professor,
                "Curso": "342 - Ciência da Informação"
            }
            dados_estruturados.append(registro)
                
    print(f"Processamento concluído. {len(dados_estruturados)} turmas mapeadas com sucesso.")
    return dados_estruturados