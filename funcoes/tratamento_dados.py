import os
import re
import pandas as pd

# ____________________________________________________
# Tabela Completa de Mapeamento Curricular (Novo + Antigo PPC)
# ____________________________________________________
DISCIPLINAS_MAPEADAS = {
    # 1ª FASE
    "CAD5103": "1ª Fase", "CIN7141": "1ª Fase", "CIN7143": "1ª Fase",
    "CIN7144": "1ª Fase", "CIN7145": "1ª Fase", "CIN7925": "1ª Fase",
    "CIN7943": "1ª Fase", "LLV7802": "1ª Fase", "MTM3110": "1ª Fase",

    # 2ª FASE
    "CIN7201": "2ª Fase", "CIN7202": "2ª Fase", "CIN7203": "2ª Fase",
    "CIN7204": "2ª Fase", "CIN7205": "2ª Fase", "CIN7206": "2ª Fase",
    "CIN7309": "2ª Fase", "CIN7412": "2ª Fase", "CIN7907": "2ª Fase", 
    "INE5111": "2ª Fase",

    # 3ª FASE
    "CIN7000": "3ª Fase", "CIN7301": "3ª Fase", "CIN7302": "3ª Fase",
    "CIN7303": "3ª Fase", "CIN7304": "3ª Fase", "CIN7306": "3ª Fase",
    "CIN7936": "3ª Fase", "HST7921": "3ª Fase", 
    "MTM3687": "3ª Fase",

    # 4ª FASE
    "CIN1111": "4ª Fase", "CIN7401": "4ª Fase", "CIN7402": "4ª Fase",
    "CIN7403": "4ª Fase", "CIN7404": "4ª Fase", "CIN7405": "4ª Fase",
    "CIN7406": "4ª Fase", "CIN7411": "4ª Fase",
    "CIN7903": "4ª Fase",

    # 5ª FASE
    "CIN7502": "5ª Fase", "CIN7504": "5ª Fase", "CIN7505": "5ª Fase",
    "CIN7906": "5ª Fase", 
    "CIN7933": "5ª Fase", "CIN7503": "5ª Fase",
    "CIN7501": "5ª Fase",

    # 6ª FASE
    "CIN7601": "6ª Fase", "CIN7602": "6ª Fase", "CIN7603": "6ª Fase",
    "CIN7604": "6ª Fase"
}

def extrair_semestre_do_nome_arquivo(caminho_pdf: str) -> str:
    nome_arquivo = os.path.basename(caminho_pdf)
    match = re.search(r"(\d{4})([12])", nome_arquivo)
    return f"{match.group(1)}.{match.group(2)}" if match else "2026.1"

def mapear_fase_e_tipo(codigo: str):
    codigo_limpo = str(codigo).strip().upper()
    if codigo_limpo in DISCIPLINAS_MAPEADAS:
        return DISCIPLINAS_MAPEADAS[codigo_limpo], "Obrigatória"
    return "Optativa", "Optativa"

def separar_horario_e_local(texto_horario_local: str):
    if not texto_horario_local or pd.isna(texto_horario_local):
        return "N/A", "N/A"

    blocos = str(texto_horario_local).split("|")
    horarios, locais = [], []

    for bloco in blocos:
        if "/" in bloco:
            partes = bloco.split("/", 1)
            horarios.append(partes[0].strip())
            locais.append(partes[1].strip())
        else:
            horarios.append(bloco.strip())
            locais.append("A definir")

    return " | ".join(horarios), " | ".join(locais)

def filtrar_turmas_invalidas(df: pd.DataFrame) -> pd.DataFrame:
    mascara_cancelada = (
        df["Nome da Disciplina"].astype(str).str.contains(r"\[Cancelada\]|cancelada", case=False, na=False) |
        df["Professor"].astype(str).str.contains(r"Disciplina Cancelada|cancelada", case=False, na=False)
    )
    mascara_intercambio = df["Nome da Disciplina"].astype(str).str.contains(r"Intercâmbio", case=False, na=False)
    
    col_horario = df["Horário/Local"] if "Horário/Local" in df.columns else df.get("Horario_Local", "")
    mascara_sem_horario = col_horario.isna() | col_horario.astype(str).str.strip().isin(["", "N/A", "A definir", "nan", "None"])

    return df[~(mascara_cancelada | mascara_intercambio | mascara_sem_horario)].copy()

def alocar_optativas_nas_fases(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "Fase" not in df.columns:
        return df

    contador_optativa = 0
    for idx, row in df.iterrows():
        if row["Fase"] == "Optativa":
            if contador_optativa % 2 == 0:
                df.at[idx, "Fase"] = "5ª Fase"
            else:
                df.at[idx, "Fase"] = "6ª Fase"
            contador_optativa += 1

    return df

# ____________________________________________________
# Análise de Código UFSC e Choques de Horário
# ____________________________________________________
def eh_turno_matutino(horario_bruto: str) -> bool:
    if not horario_bruto or pd.isna(horario_bruto):
        return True
    s = str(horario_bruto)
    codigos_manha = [".0730", ".0820", ".0910", ".1010", ".1100"]
    return any(c in s for c in codigos_manha)

def extrair_slots_horario_bruto(horario_bruto: str) -> list:
    if not horario_bruto or pd.isna(horario_bruto):
        return []

    slots = []
    matches = re.findall(r'(\d)\.(\d{4})-(\d)', str(horario_bruto))
    
    mapa_sequencia = {
        "0730": ["0730", "0820", "0910", "1010", "1100"],
        "0820": ["0820", "0910", "1010", "1100", "1150"],
        "0910": ["0910", "1010", "1100", "1150"],
        "1010": ["1010", "1100", "1150"],
        "1330": ["1330", "1420", "1510", "1620", "1710"],
        "1420": ["1420", "1510", "1620", "1710", "1800"],
        "1830": ["1830", "1920", "2020", "2110"],
        "1920": ["1920", "2020", "2110"],
        "2020": ["2020", "2110"],
    }

    for dia, hor_inicio, qtd_horas in matches:
        qtd = int(qtd_horas)
        seq = mapa_sequencia.get(hor_inicio, [hor_inicio])
        for h in seq[:qtd]:
            slots.append((dia, h))

    return slots

def tem_choque_com_fase_bruto(df: pd.DataFrame, col_horario: str, codigo_alvo: str, turma_alvo: str, fase_destino: str, slots_turma: list) -> bool:
    if not slots_turma:
        return False

    outras_turmas = df[
        (df["Fase"] == fase_destino) & 
        ~((df["Código da Disciplina"] == codigo_alvo) & (df["Turma"] == turma_alvo))
    ]

    slots_fase = set()
    for _, row in outras_turmas.iterrows():
        hor = row.get(col_horario, "")
        for slot in extrair_slots_horario_bruto(hor):
            slots_fase.add(slot)

    for slot in slots_turma:
        if slot in slots_fase:
            return True

    return False

def ajustar_fases_especiais_e_choques(df: pd.DataFrame, col_horario: str) -> pd.DataFrame:
    if df.empty:
        return df

    for idx, row in df.iterrows():
        codigo = str(row.get("Código da Disciplina", "")).strip().upper()
        horario_bruto = str(row.get(col_horario, ""))
        turma = str(row.get("Turma", ""))
        matutino = eh_turno_matutino(horario_bruto)
        slots = extrair_slots_horario_bruto(horario_bruto)

        # Regra CIN7412: Matutino -> 4ª Fase | Noturno -> 2ª Fase
        if codigo == "CIN7412":
            fase_inicial = "4ª Fase" if matutino else "2ª Fase"
            fase_inversa = "2ª Fase" if matutino else "4ª Fase"

            if tem_choque_com_fase_bruto(df, col_horario, codigo, turma, fase_inicial, slots):
                df.at[idx, "Fase"] = fase_inversa
            else:
                df.at[idx, "Fase"] = fase_inicial

        # Regra CIN7309: Matutino -> 3ª Fase | Noturno -> 2ª Fase
        elif codigo == "CIN7309":
            fase_inicial = "3ª Fase" if matutino else "2ª Fase"
            fase_inversa = "2ª Fase" if matutino else "3ª Fase"

            if tem_choque_com_fase_bruto(df, col_horario, codigo, turma, fase_inicial, slots):
                df.at[idx, "Fase"] = fase_inversa
            else:
                df.at[idx, "Fase"] = fase_inicial

    return df

def duplicar_ine5111_para_ambas_fases(df: pd.DataFrame) -> pd.DataFrame:
    """Garante que a disciplina INE5111 seja projetada tanto na 2ª quanto na 4ª Fase para visualização nas grades."""
    if df.empty:
        return df

    novas_linhas = []
    for idx, row in df.iterrows():
        codigo = str(row.get("Código da Disciplina", "")).strip().upper()
        if codigo == "INE5111":
            # Cria registro adicional alocado na 4ª Fase
            copia_4a = row.copy()
            copia_4a["Fase"] = "4ª Fase"
            novas_linhas.append(copia_4a)

    if novas_linhas:
        df = pd.concat([df, pd.DataFrame(novas_linhas)], ignore_index=True)

    return df

def enriquecer_com_tipo_nucleo(df: pd.DataFrame, supabase_client=None) -> pd.DataFrame:
    if df.empty or supabase_client is None:
        if "Tipo de Disciplina" not in df.columns:
            df["Tipo de Disciplina"] = "Específico"
        return df

    try:
        res = supabase_client.table("disciplinas_matriz").select("*").execute()
        if res.data:
            df_matriz = pd.DataFrame(res.data)
            col_matriz = "codigo" if "codigo" in df_matriz.columns else "codigo_disciplina"
            df_matriz = df_matriz.rename(columns={col_matriz: "Código da Disciplina"})

            df = pd.merge(df, df_matriz, on="Código da Disciplina", how="left")

            if "tipo_nucleo" in df.columns:
                df["Tipo de Disciplina"] = df["tipo_nucleo"].fillna("Específico")
                df.drop(columns=["tipo_nucleo"], inplace=True)

    except Exception:
        if "Tipo de Disciplina" not in df.columns:
            df["Tipo de Disciplina"] = "Específico"

    return df

def aplicar_tratamento_completo(dados_brutos: list, caminho_pdf: str, supabase_client=None) -> pd.DataFrame:
    df = pd.DataFrame(dados_brutos)
    if df.empty:
        return df

    # 1. Filtro inicial de turmas descartáveis
    df = filtrar_turmas_invalidas(df)

    # 2. Inserção do Semestre
    df["Semestre"] = extrair_semestre_do_nome_arquivo(caminho_pdf)

    # 3. Mapeamento Unificado de Fase e Tipo (Usa Mapeamento Completo)
    fases_tipos = df["Código da Disciplina"].apply(mapear_fase_e_tipo)
    df["Fase"] = [item[0] for item in fases_tipos]
    df["Tipo"] = [item[1] for item in fases_tipos]

    # 4. Ajuste Dinâmico de Turnos e Anti-Choque (DEVE RODAR ANTES DA SEPARAÇÃO DE HORÁRIO/LOCAL)
    col_origem_horario = "Horário/Local" if "Horário/Local" in df.columns else "Horario_Local"
    df = ajustar_fases_especiais_e_choques(df, col_horario=col_origem_horario)

    # 5. Duplicação de projeção para INE5111 (2ª e 4ª Fase)
    df = duplicar_ine5111_para_ambas_fases(df)

    # 6. Divisão de Horário e Local para Formato Legível
    col_origem = df["Horário/Local"] if "Horário/Local" in df.columns else df.get("Horario_Local", "")
    horarios_locais = col_origem.apply(separar_horario_e_local)
    df["Horário"] = [hl[0] for hl in horarios_locais]
    df["Local"] = [hl[1] for hl in horarios_locais]

    # 7. Alocação de Optativas Legítimas
    df = alocar_optativas_nas_fases(df)

    # 8. Enriquecimento de Núcleo via Supabase (Comum vs. Específico)
    df = enriquecer_com_tipo_nucleo(df, supabase_client)

    # 9. Reordenação e seleção de colunas finais
    colunas_finais = [
        "Semestre", "Código da Disciplina", "Turma", "Nome da Disciplina",
        "Fase", "Tipo", "Tipo de Disciplina", "Horas Aula", "Ofertas", "Horário", "Local", "Professor"
    ]
    colunas_presentes = [c for c in colunas_finais if c in df.columns]

    return df[colunas_presentes]