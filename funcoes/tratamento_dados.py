import os
import re
import pandas as pd


# -------------------------------------------
# Extração do Semestre via Nome do PDF
# -------------------------------------------
def extrair_semestre_do_nome_arquivo(caminho_pdf: str) -> str:
    nome_arquivo = os.path.basename(caminho_pdf)
    match = re.search(r"(\d{4})([12])", nome_arquivo)
    if match:
        ano, periodo = match.groups()
        return f"{ano}.{periodo}"
    return "2026.1"


# -------------------------------------------
# Mapeamento de Fase e Tipo de Disciplina
# -------------------------------------------
def mapear_fase_e_tipo(codigo: str):
    codigo = str(codigo).strip().upper()

    # Exceções mapeadas manualmente
    excecoes = {
        # --- 1ª Fase ---
        "CIN7925": ("1ª Fase", "Obrigatória"),
        "CIN7943": ("1ª Fase", "Obrigatória"),
        "LLV7802": ("1ª Fase", "Obrigatória"),
        "MTM3110": ("1ª Fase", "Obrigatória"),
        "CAD5103": ("1ª Fase", "Obrigatória"),
        # --- 2ª Fase ---
        "INE5111": ("2ª Fase", "Obrigatória"),
        "CIN7907": ("2ª Fase", "Obrigatória"),
        "CIN7412": ("2ª Fase", "Obrigatória"),
        # --- 3ª Fase ---
        "CIN7936": ("3ª Fase", "Obrigatória"),
        "HST7921": ("3ª Fase", "Obrigatória"),
        # --- Optativas Específicas ---
        "CIN7903": ("Optativa", "Optativa"),
    }

    if codigo in excecoes:
        return excecoes[codigo]

    # Regra Geral para disciplinas CIN7
    if codigo.startswith("CIN"):
        match = re.search(r"CIN7(\d)", codigo)
        if match:
            digito_fase = match.group(1)
            if digito_fase == "9":
                return "Optativa", "Optativa"
            elif digito_fase in ["1", "2", "3", "4", "5", "6"]:
                return f"{digito_fase}ª Fase", "Obrigatória"

    return "Outros / Eletiva", "Optativa"


# -------------------------------------------
# Divisão da Coluna Horario/Local
# -------------------------------------------
def separar_horario_e_local(texto_horario_local: str):
    if not texto_horario_local or pd.isna(texto_horario_local):
        return "N/A", "N/A"

    blocos = str(texto_horario_local).split("|")
    horarios = []
    locais = []

    for bloco in blocos:
        if "/" in bloco:
            partes = bloco.split("/", 1)
            horarios.append(partes[0].strip())
            locais.append(partes[1].strip())
        else:
            horarios.append(bloco.strip())
            locais.append("A definir")

    string_horario = " | ".join(horarios)
    string_local = " | ".join(locais)

    return string_horario, string_local


# -------------------------------------------
# LÓGICA ANTI-CONFLITO DE HORÁRIOS UFSC
# -------------------------------------------
def extrair_slots_horario(horario_str: str) -> set:
    """
    Transforma uma string como '2.0820-2 | 4.1010-2' em um conjunto de slots únicos.
    Exemplo: '2.0820-2' gera o conjunto {('2', '0820'), ('2', '0910')} para comparação exata.
    """
    slots = set()
    if not horario_str or horario_str in ["N/A", "A definir"]:
        return slots

    blocos = str(horario_str).split("|")
    for bloco in blocos:
        bloco = bloco.strip()
        match = re.search(r"(\d)\.(\d{4})-(\d)", bloco)
        if match:
            dia, hora_inicio, num_aulas = match.groups()
            num_aulas = int(num_aulas)
            
            # Mapeamento aproximado de blocos de aulas por horário inicial da UFSC
            hora_int = int(hora_inicio)
            for i in range(num_aulas):
                # Cada slot é identificado pelo (Dia, Bloco_Horário)
                slots.add((dia, hora_int + (i * 50)))  # Incremento simplificado por bloco
    return slots


def tem_choque_de_horario(horario_optativa: str, lista_horarios_obrigatorias: list) -> bool:
    """
    Retorna True se o horário da optativa colidir com qualquer disciplina obrigatória da fase.
    """
    slots_optativa = extrair_slots_horario(horario_optativa)
    if not slots_optativa:
        return False  # Sem horário definido, não há como confirmar choque

    for hor_obrig in lista_horarios_obrigatorias:
        slots_obrig = extrair_slots_horario(hor_obrig)
        # Se a interseção de slots de horário não for vazia, há choque!
        if slots_optativa.intersection(slots_obrig):
            return True

    return False


def alocar_optativas_nas_fases(df: pd.DataFrame) -> pd.DataFrame:
    """
    Garante o preenchimento de optativas na 5ª e 6ª fases sem gerar choques com obrigatórias.
    """
    print("[Tratamento] Executando algoritmo de alocação de Optativas sem choque...")

    # Mapeia horários das disciplinas obrigatórias das fases 5 e 6
    obrigatorias_5a = df[(df["Fase"] == "5ª Fase") & (df["Tipo"] == "Obrigatória")]["Horário"].tolist()
    obrigatorias_6a = df[(df["Fase"] == "6ª Fase") & (df["Tipo"] == "Obrigatória")]["Horário"].tolist()

    for idx, linha in df.iterrows():
        if linha["Tipo"] == "Optativa":
            horario_optativa = linha["Horário"]

            # Tenta alocar na 5ª Fase primeiro
            if not tem_choque_de_horario(horario_optativa, obrigatorias_5a):
                df.at[idx, "Fase"] = "5ª Fase (Optativa)"
                # Adiciona o horário para não alocar outra optativa no mesmo slot na 5ª fase
                obrigatorias_5a.append(horario_optativa)
            
            # Se deu choque na 5ª, tenta alocar na 6ª Fase
            elif not tem_choque_de_horario(horario_optativa, obrigatorias_6a):
                df.at[idx, "Fase"] = "6ª Fase (Optativa)"
                obrigatorias_6a.append(horario_optativa)

    return df

# -------------------------------------------
# Filtro de Turmas Canceladas / Intercâmbio / Sem Horário
# -------------------------------------------
def filtrar_turmas_invalidas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove turmas que foram canceladas, programas de intercâmbio ou
    que não possuem horários definidos/válidos.
    """
    total_inicial = len(df)

    # 1. Filtra turmas com '[Cancelada]' no Nome ou no Professor
    mascara_cancelada = (
        df["Nome da Disciplina"].astype(str).str.contains(r"\[Cancelada\]|cancelada", case=False, na=False) |
        df["Professor"].astype(str).str.contains(r"Disciplina Cancelada|cancelada", case=False, na=False)
    )

    # 2. Filtra turmas de Intercâmbio (que não têm grade presencial)
    mascara_intercambio = df["Nome da Disciplina"].astype(str).str.contains(r"Intercâmbio", case=False, na=False)

    # 3. Filtra horários nulos ou 'A definir' / 'N/A'
    coluna_horario = df["Horário/Local"] if "Horário/Local" in df.columns else df.get("Horario_Local", df.get("Horário", ""))
    mascara_sem_horario = (
        coluna_horario.isna() |
        coluna_horario.astype(str).str.strip().isin(["", "N/A", "A definir", "nan", "None"])
    )

    # Combina todas as condições de exclusão
    mascara_remover = mascara_cancelada | mascara_intercambio | mascara_sem_horario
    
    # Mantém apenas as turmas válidas
    df_limpo = df[~mascara_remover].copy()

    removidas = total_inicial - len(df_limpo)
    if removidas > 0:
        print(f"[Tratamento] 🚫 {removidas} turmas inválidas/canceladas/intercâmbio foram descartadas.")

    return df_limpo
# -------------------------------------------
# Pipeline de Tratamento do DataFrame
# -------------------------------------------
def aplicar_tratamento_completo(dados_brutos: list, caminho_pdf: str) -> pd.DataFrame:
    print("\n[Tratamento] Executando enriquecimento e divisão de colunas...")
    df = pd.DataFrame(dados_brutos)

    if df.empty:
        return df

    # --- 1. FILTRAGEM DE TURMAS INVALIDEZ (NOVO) ---
    df = filtrar_turmas_invalidas(df)

    # Inserção da Coluna de Semestre
    df["Semestre"] = extrair_semestre_do_nome_arquivo(caminho_pdf)

    # Mapeamento de Fase e Tipo
    fases_tipos = df["Código da Disciplina"].apply(mapear_fase_e_tipo)
    df["Fase"] = [item[0] for item in fases_tipos]
    df["Tipo"] = [item[1] for item in fases_tipos]

    # Separação de Horário e Local
    coluna_origem = df["Horário/Local"] if "Horário/Local" in df.columns else df.get("Horario_Local", "")
    horarios_locais = coluna_origem.apply(separar_horario_e_local)

    df["Horário"] = [hl[0] for hl in horarios_locais]
    df["Local"] = [hl[1] for hl in horarios_locais]

    # --- ALOCAÇÃO AUTOMÁTICA DE OPTATIVAS ---
    df = alocar_optativas_nas_fases(df)

    # Reordenação limpa das colunas
    colunas_finais = [
        "Semestre", "Código da Disciplina", "Turma", "Nome da Disciplina",
        "Fase", "Tipo", "Horas Aula", "Ofertas", "Horário", "Local", "Professor"
    ]

    df = df[colunas_finais]
    print(f"[Tratamento] {len(df)} turmas válidas processadas com sucesso!")
    return df