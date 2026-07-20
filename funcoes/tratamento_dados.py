import os
import re
import pandas as pd


# -------------------------------------------
# Extração do Semestre via Nome do PDF
# -------------------------------------------
# Identifica o padrão numérico do semestre no nome do arquivo (ex: CADASTRO_TURMAS_20261.pdf)
# e formata para o padrão visual '2026.1'.
def extrair_semestre_do_nome_arquivo(caminho_pdf: str) -> str:
    nome_arquivo = os.path.basename(caminho_pdf)
    match = re.search(r"(\d{4})([12])", nome_arquivo)
    if match:
        ano, periodo = match.groups()
        return f"{ano}.{periodo}"
    return "2026.1"  # Valor fallback padrão


# -------------------------------------------
# Mapeamento de Fase e Tipo de Disciplina
# -------------------------------------------
# Avalia o código da disciplina aplicando regras para exceções de departamentos
# e regras gerais baseadas nos dígitos para identificar Fase e se é Obrigatória/Optativa.
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
# Divisão da Coluna Horario/Local em 'Horário' e 'Local'
# -------------------------------------------
# Separa a string combinada (ex: '5.2020-2 / CCE-CCE129' ou com múltiplos blocos '|')
# extraindo o código do horário para uma coluna e o código da sala/prédio para outra.
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
# Pipeline de Tratameto do DataFrame Pandas
# -------------------------------------------
# Orquestra a adição da coluna Semestre, o mapeamento de Fase/Tipo,
# a separação de Horário/Local e reordena as colunas finais.
def aplicar_tratamento_completo(dados_brutos: list, caminho_pdf: str) -> pd.DataFrame:
    print("\n[Tratamento] Executando enriquecimento e divisão de colunas...")
    df = pd.DataFrame(dados_brutos)

    if df.empty:
        return df

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

    # Reordenação limpa das colunas
    colunas_finais = [
        "Semestre", "Código da Disciplina", "Turma", "Nome da Disciplina",
        "Fase", "Tipo", "Horas Aula", "Ofertas", "Horário", "Local", "Professor"
    ]
    
    df = df[colunas_finais]
    print(f"[Tratamento] {len(df)} turmas processadas com sucesso!")
    return df