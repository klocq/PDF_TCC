import re

def processar_texto_bruto(texto_bruto):
    dados_estruturados = []
    linhas = texto_bruto.split("\n")
    
    # Expressões regulares estáveis de ancoragem
    padrao_inicio = re.compile(r'^([A-Z]{3}\d{4})\s+(\d{5}[A-Z]?)')
    padrao_horario_ufsc = re.compile(r'(\d\.\d{4}-\d\s*/\s*[A-Z0-9-]+(?:\s+[A-Z]\b)?)')
    
    # Lista negra definitiva: se a linha contiver QUALQUER uma dessas palavras, NÃO é um professor!
    palavras_proibidas_professor = {
        "VAGAS", "OFERTADAS", "OCUPADAS", "ALUNOS", "ESPECIAIS", "SALDO", 
        "PEDIDOS", "SEM", "VAGA", "PROFESSORES", "CURSO", "DISCIPLINA", "NOME"
    }
    
    linha_acumulada = ""

    for i, linha in enumerate(linhas):
        linha = linha.strip()
        
        if not linha:
            continue
            
        # 1. FILTRO DE CABEÇALHOS DO DOCUMENTO
        linha_maiuscula = linha.upper()
        if ("SEMESTRE:" in linha_maiuscula or 
            "CADASTRO DE TURMAS" in linha_maiuscula or 
            "SETIC" in linha_maiuscula or
            "PÁGINA:" in linha_maiuscula):
            continue
            
        # 2. TRATAMENTO DE LINHAS ÓRFÃS (Horários extras ou Professores deslocados)
        if not padrao_inicio.search(linha) and not linha_acumulada:
            if dados_estruturados:
                ultimo_registro = dados_estruturados[-1]
                match_horario_extra = padrao_horario_ufsc.findall(linha)
                
                if match_horario_extra:
                    horarios_str = " | ".join([h.strip() for h in match_horario_extra])
                    if ultimo_registro["Horário/Local"] == "A definir":
                        ultimo_registro["Horário/Local"] = horarios_str
                    else:
                        ultimo_registro["Horário/Local"] += " | " + horarios_str
                else:
                    # Limpa identificadores de curso residuais como 342
                    texto_limpo = re.sub(r'\b342\b', '', linha).strip()
                    texto_limpo = re.sub(r'\s+', ' ', texto_limpo)
                    
                    if texto_limpo and not texto_limpo.isdigit() and len(texto_limpo) > 3:
                        if "[CANCELADA]" not in texto_limpo.upper():
                            
                            # --- VALIDAÇÃO CRUCIAL CONTRA PALAVRAS FANTASMAS ---
                            # Quebra a linha em palavras e checa se alguma bate com a lista negra
                            palavras_da_linha = set(re.findall(r'[A-ZÁÉÍÓÚÂÊÔÇÀ-]+', texto_limpo.upper()))
                            
                            # Se a interseção encontrar qualquer palavra proibida, ignora a linha!
                            if palavras_da_linha.intersection(palavras_proibidas_professor):
                                continue
                            
                            # Se passou no teste, é um professor legítimo!
                            if ultimo_registro["Professor"] == "A contratar" or not ultimo_registro["Professor"]:
                                ultimo_registro["Professor"] = texto_limpo
                            else:
                                if texto_limpo not in ultimo_registro["Professor"]:
                                    ultimo_registro["Professor"] += " e " + texto_limpo
            continue

        # 3. PROCESSAMENTO DA LINHA PRINCIPAL DA DISCIPLINA
        if linha_acumulada:
            linha_completa = linha_acumulada + " " + linha
        else:
            linha_completa = linha

        match_inicio = padrao_inicio.search(linha_completa)
        
        if match_inicio:
            if not re.search(r'\d+\s+\d+\s+\d+\s+\d+\s+\d+', linha_completa):
                linha_acumulada = linha_completa
                continue
            
            linha_acumulada = ""
            
            codigo = match_inicio.group(1)
            turma = match_inicio.group(2)
            
            resto = linha_completa.replace(codigo, "").replace(turma, "").strip()
            match_numeros = re.search(r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', resto)
            
            if match_numeros:
                bloco_numeros = match_numeros.group(0)
                numeros = bloco_numeros.split()
                
                horas_aula = numeros[0]
                ofertas = numeros[1]
                
                idx_numeros = resto.find(bloco_numeros)
                nome_disciplina = resto[:idx_numeros].strip()
                nome_disciplina = re.sub(r'\s+', ' ', nome_disciplina)
                
                depois_dos_numeros = resto[idx_numeros + len(bloco_numeros):].strip()
                todos_horarios = padrao_horario_ufsc.findall(depois_dos_numeros)
                
                horario_local = "A definir"
                professor = "A contratar"
                
                if todos_horarios:
                    horario_local = " | ".join([h.strip() for h in todos_horarios])
                    
                    texto_sem_horarios = depois_dos_numeros
                    for h in todos_horarios:
                        texto_sem_horarios = texto_sem_horarios.replace(h, "")
                    
                    texto_prof = re.sub(r'\b342\b', '', texto_sem_horarios)
                    texto_professor_limpo = re.sub(r'^\s*\d+\s*', '', texto_prof).strip()
                    texto_professor_limpo = re.sub(r'\s+', ' ', texto_professor_limpo).strip()
                    
                    if texto_professor_limpo and not texto_professor_limpo.isdigit() and len(texto_professor_limpo) > 2:
                        # Valida se o professor da linha principal não pegou lixo por acidente
                        palavras_da_linha = set(re.findall(r'[A-ZÁÉÍÓÚÂÊÔÇÀ-]+', texto_professor_limpo.upper()))
                        if not palavras_da_linha.intersection(palavras_proibidas_professor):
                            professor = texto_professor_limpo
                
                if "A CONTRATAR" in professor.upper() or not professor:
                    professor = "A contratar"
                
                if "[CANCELADA]" in linha_completa.upper():
                    professor = "Disciplina Cancelada"
                    horario_local = "N/A"
                
                registro = {
                    "Código da Disciplina": codigo,
                    "Turma": turma,
                    "Nome da Disciplina": nome_disciplina,
                    "Horas Aula": horas_aula,
                    "Ofertas": ofertas,
                    "Horário/Local": horario_local,
                    "Professor": professor,
                    "Curso": "342 - Ciência da Informação"
                }
                dados_estruturados.append(registro)

    # 4. GERAÇÃO DO ARQUIVO TEXTUAL FINAL
    # 4. GERAÇÃO DO ARQUIVO TEXTUAL FINAL (Voltando um nível com ../)
    with open("../resultados/relatorio_auditoria.txt", "w", encoding="utf-8") as f:
        f.write("="*60 + "\n")
        f.write("RELATÓRIO DE AUDITORIA DAS TURMAS EXTRAÍDAS (VERSÃO IMUNE A CABEÇALHOS)\n")
        f.write("="*60 + "\n")
        
        for idx, reg in enumerate(dados_estruturados, 1):
            bloco_texto = (
                f"[TURMA DETECTADA Nº {idx}]\n"
                f"  • CÓDIGO/TURMA: {reg['Código da Disciplina']} | {reg['Turma']}\n"
                f"  • DISCIPLINA:  {reg['Nome da Disciplina']}\n"
                f"  • H.A. / VAGAS: {reg['Horas Aula']} H.A. | {reg['Ofertas']} Vagas\n"
                f"  • HORÁRIOS:    {reg['Horário/Local']}\n"
                f"  • PROFESSOR:   {reg['Professor']}\n"
                f"{'-'*50}\n"
            )
            #print(bloco_texto, end="")
            f.write(bloco_texto)
            
    print(f"\n[SUCESSO] Relatório imune salvo em 'relatorio_auditoria.txt'.")
    print(dados_estruturados)
    return dados_estruturados