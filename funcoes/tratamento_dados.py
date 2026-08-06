import os
import re
import pandas as pd
from banco import obter_matriz_por_curriculo


def extrair_semestre_do_nome_arquivo(caminho_pdf: str) -> str:
    """Extrai o ano/semestre (ex: 2026.1) a partir do nome do arquivo PDF."""
    if not caminho_pdf:
        return "2026.1"
    nome_arquivo = os.path.basename(caminho_pdf)
    match = re.search(r"(\d{4})([12])", nome_arquivo)
    return f"{match.group(1)}.{match.group(2)}" if match else "2026.1"


def carregar_mapa_matriz_curricular(curriculo: str) -> dict:
    """
    Busca no Supabase a matriz curricular para o currículo informado
    e constrói um dicionário de mapeamento no formato:
    { 'CODIGO_DISCIPLINA': (Fase, Tipo) }
    """
    df_matriz = obter_matriz_por_curriculo(curriculo)
    mapa = {}

    if df_matriz is not None and not df_matriz.empty:
        col_codigo = "codigo_disciplina" if "codigo_disciplina" in df_matriz.columns else "codigo"
        for _, row in df_matriz.iterrows():
            cod = str(row.get(col_codigo, "")).strip().upper()
            fase = str(row.get("fase", "Optativa")).strip()
            tipo_bruto = str(row.get("tipo", "Op")).strip()
            nucleo = str(row.get("nucleo", "Comun")).strip()

            # Padronização amigável de 'Ob' e 'Op'
            if tipo_bruto.upper() in ["OB", "OBRIGATÓRIA", "OBRIGATORIA"]:
                tipo = "Obrigatória"
            elif tipo_bruto.upper() in ["OP", "OPTATIVA"]:
                tipo = "Optativa"
            else:
                tipo = tipo_bruto

            mapa[cod] = (fase, tipo, nucleo)

    return mapa


def separar_horario_e_local(texto_horario_local: str):
    """Separa strings do formato 'Horário / Local | Horário / Local' em colunas individuais."""
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
    """Remove turmas canceladas, de intercâmbio ou sem horário/local definidos."""
    mascara_cancelada = (
        df["Nome da Disciplina"].astype(str).str.contains(r"\[Cancelada\]|cancelada", case=False, na=False) |
        df["Professor"].astype(str).str.contains(r"Disciplina Cancelada|cancelada", case=False, na=False)
    )
    mascara_intercambio = df["Nome da Disciplina"].astype(str).str.contains(r"Intercâmbio", case=False, na=False)
    
    col_horario = df["Horário/Local"] if "Horário/Local" in df.columns else df.get("Horario_Local", "")
    mascara_sem_horario = col_horario.isna() | col_horario.astype(str).str.strip().isin(["", "N/A", "A definir", "nan", "None"])

    return df[~(mascara_cancelada | mascara_intercambio | mascara_sem_horario)].copy()


def alocar_optativas_nas_fases(df: pd.DataFrame) -> pd.DataFrame:
    """Distribui alternadamente as disciplinas optativas entre a 5ª e a 6ª Fase para exibição."""
    if df.empty or "Fase" not in df.columns:
        return df

    contador_optativa = 0
    for idx, row in df.iterrows():
        if row["Fase"] in ["Optativa", "Optativas"]:
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
    """Aplica regras de alocação anti-choque para disciplinas específicas como CIN7412 e CIN7309."""
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
            copia_4a = row.copy()
            copia_4a["Fase"] = "4ª Fase"
            novas_linhas.append(copia_4a)

    if novas_linhas:
        df = pd.concat([df, pd.DataFrame(novas_linhas)], ignore_index=True)

    return df


# ____________________________________________________
# Função Principal do Módulo de Tratamento
# ____________________________________________________
def aplicar_tratamento_completo(dados_brutos: list, caminho_pdf: str, supabase_client=None, curriculo: str = "20161") -> pd.DataFrame:
    df = pd.DataFrame(dados_brutos)
    if df.empty:
        return df

    # 1. Filtro inicial de turmas descartáveis
    df = filtrar_turmas_invalidas(df)

    # 2. Inserção do Semestre
    df["Semestre"] = extrair_semestre_do_nome_arquivo(caminho_pdf)

    # 3. Busca dinâmica da matriz no Supabase para o currículo selecionado ('20161' ou '20261')
    mapa_matriz = carregar_mapa_matriz_curricular(curriculo)

    def mapear_fase_e_tipo_dinamico(codigo: str):
        cod_limpo = str(codigo).strip().upper()
        if cod_limpo in mapa_matriz:
            return mapa_matriz[cod_limpo]
        return "Optativa", "Optativa"

    # Mapeamento de Fase e Tipo (Obrigatória/Optativa) via banco de dados
    fases_tipos = df["Código da Disciplina"].apply(mapear_fase_e_tipo_dinamico)
    df["Fase"] = [item[0] for item in fases_tipos]
    df["Tipo"] = [item[1] for item in fases_tipos]

    # 4. Ajuste Dinâmico de Turnos e Anti-Choque
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

    # 8. Reordenação e seleção de colunas finais
    colunas_finais = [
        "Semestre", "Código da Disciplina", "Turma", "Nome da Disciplina",
        "Fase", "Tipo", "Horas Aula", "Ofertas", "Horário", "Local", "Professor"
    ]
    colunas_presentes = [c for c in colunas_finais if c in df.columns]

    return df[colunas_presentes]