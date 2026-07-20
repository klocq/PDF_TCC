import re
import pandas as pd

# 1. Dicionário oficial e corrigido do Novo Currículo (PPC 2025/2026)
DISCIPLINAS_NOVO_CURRICULO = {
    # --- 1ª FASE ---
    "CAD5103": 1,  # Administração I
    "CIN7141": 1,  # Lógica Instrumental I
    "CIN7143": 1,  # Empreendedorismo I
    "CIN7144": 1,  # Tutoria Acadêmica I
    "CIN7145": 1,  # Gestão da Informação
    "CIN7925": 1,  # Introdução a Algoritmos
    "CIN7943": 1,  # Experiência do Usuário - UX
    "LLV7802": 1,  # Leitura e Produção de Texto
    "MTM3110": 1,  # Cálculo I

    # --- 2ª FASE ---
    "CIN7201": 2,  # Sistemas de Organização do Conhecimento
    "CIN7204": 2,  # Tutoria Acadêmica II
    "CIN7309": 2,  # Gestão de Processos Organizacionais
    "CIN7412": 2,  # Marketing da Informação
    "CIN7907": 2,  # Lógica Aplicada I
    "INE5111": 2,  # Estatística Aplicada I

    # --- 3ª FASE ---
    "CIN7000": 3,  # Laboratório de Empreendimentos Sociais
    "CIN7301": 3,  # Introdução à Representação Temática
    "CIN7302": 3,  # Introdução à Representação Descritiva
    "CIN7304": 3,  # Introdução à Bancos de Dados
    "CIN7501": 3,  # Arquitetura da Informação e Usabilidade
    "CIN7936": 3,  # Proteção de Dados Pessoais
    "MTM3687": 3,  # Aprendizado de Máquina Aplicado

    # --- 4ª FASE ---
    "CIN1111": 4,  # Fontes de Informação Tecnológica
    "CIN7401": 4,  # Estudos Métricos da Informação
    "CIN7403": 4,  # Acessibilidade e Inclusão Digital
    "CIN7404": 4,  # Planejamento Estratégico
    "CIN7411": 4,  # Análise Exploratória de Dados
    "CIN7503": 4,  # Bancos de Dados
    "CIN7903": 4,  # Inteligência Competitiva
    "CIN7938": 4,  # Segurança da Informação
    "HST7921": 4,  # História do Brasil Contemporâneo

    # --- 5ª FASE ---
    "CIN7502": 5,  # Mineração de Texto
    "CIN7504": 5,  # Gerenciamento de Projetos
    "CIN7505": 5,  # Estágio em Ciência da Informação
    "CIN7933": 5,  # Gestão da Inovação

    # --- 6ª FASE ---
    "CIN7601": 6,  # Linked Data
    "CIN7602": 6,  # Mídias Sociais
    "CIN7603": 6,  # Empreendedorismo II
    "CIN7604": 6,  # TCC
}


def aplicar_fases_novas(dados_estruturados):
    """
    Recebe a lista de dicionários das turmas extraídas do PDF
    e adiciona a fase correta do currículo de 2026.1
    """
    df = pd.DataFrame(dados_estruturados)

    if df.empty:
        return []

    # Garante que a coluna de código esteja limpa e formatada como texto
    df['Código da Disciplina'] = df['Código da Disciplina'].astype(str).str.strip()

    # Aplica o mapeamento da fase do Novo Currículo.
    df['Fase'] = df['Código da Disciplina'].map(DISCIPLINAS_NOVO_CURRICULO).fillna("Optativa")

    # Converte de volta para lista de dicionários para o resto do código
    return df.to_dict(orient="records")


def processar_texto_bruto(texto_bruto):
    dados_estruturados = []
    linhas = texto_bruto.split("\n")

    # Expressões regulares estáveis de ancoragem
    padrao_inicio = re.compile(r'^([A-Z]{3}\d{4})\s+(\d{5}[A-Z]?)')
    padrao_horario_ufsc = re.compile(r'(\d\.\d{4}-\d\s*/\s*[A-Z0-9-]+(?:\s+[A-Z]\b)?)')

    # Lista negra de palavras para não confundir cabeçalho com nome do professor
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

        # 2. TRATAMENTO DE LINHAS ÓRFÃS
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
                    texto_limpo = re.sub(r'\b342\b', '', linha).strip()
                    texto_limpo = re.sub(r'\s+', ' ', texto_limpo)

                    if texto_limpo and not texto_limpo.isdigit() and len(texto_limpo) > 3:
                        if "[CANCELADA]" not in texto_limpo.upper():
                            palavras_da_linha = set(re.findall(r'[A-ZÁÉÍÓÚÂÊÔÇÀ-]+', texto_limpo.upper()))

                            if palavras_da_linha.intersection(palavras_proibidas_professor):
                                continue

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

    # Aplicação do mapeamento de currículo
    dados_estruturados = aplicar_fases_novas(dados_estruturados)

    print(f"[Processador] {len(dados_estruturados)} turmas estruturadas com sucesso.")
    return dados_estruturados