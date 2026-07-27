import re
import pandas as pd

def parsear_horarios_detalhados(string_horario):
    """
    Decodifica strings de horário no padrão UFSC (ex: '2.0820-2 / 4.1010-2')
    em uma lista de tuplas: (dia_semana, bloco_horario).
    """
    if not string_horario or pd.isna(string_horario) or str(string_horario).strip() == "":
        return []

    slots = []
    padrao = re.compile(r'(\d)\.(\d{4})-(\d)')
    
    mapa_horarios = {
        "0730": ["07:30", "08:20", "09:10", "10:10", "11:00"],
        "0820": ["08:20", "09:10", "10:10", "11:00", "11:50"],
        "0910": ["09:10", "10:10", "11:00", "11:50"],
        "1010": ["10:10", "11:00", "11:50"],
        "1330": ["13:30", "14:20", "15:10", "16:20", "17:10"],
        "1420": ["14:20", "15:10", "16:20", "17:10", "18:00"],
        "1510": ["15:10", "16:20", "17:10", "18:00"],
        "1620": ["16:20", "17:10", "18:00"],
        "1830": ["18:30", "19:20", "20:20", "21:10"],
        "1920": ["19:20", "20:20", "21:10", "22:00"],
        "2020": ["20:20", "21:10", "22:00"],
    }
    
    dias_semana = {
        "2": "Segunda", "3": "Terça", "4": "Quarta",
        "5": "Quinta", "6": "Sexta", "7": "Sábado"
    }

    partes = str(string_horario).split('/')
    for parte in partes:
        match = padrao.search(parte.strip())
        if match:
            dia, hora_inicio, qtd_aulas = match.groups()
            dia_nome = dias_semana.get(dia, f"{dia}ª")
            qtd = int(qtd_aulas)

            subhorarios = mapa_horarios.get(hora_inicio, [hora_inicio])
            for i in range(min(qtd, len(subhorarios))):
                slots.append((dia_nome, subhorarios[i]))

    return slots


def detectar_todos_conflitos(df):
    """
    Audita o DataFrame de turmas e retorna três listas de conflitos:
    1. Conflitos de Professor (ignorando 'PROFESSOR A CONTRATAR', 'A DEFINIR', etc.)
    2. Conflitos de Sala/Local (ignorando 'AUX-ALOCAR', 'A DEFINIR', etc.)
    3. Conflitos de Horário na Mesma Fase
    """
    conflitos_professor = []
    conflitos_sala = []
    conflitos_fase = []

    if df.empty:
        return conflitos_professor, conflitos_sala, conflitos_fase

    col_prof = "Professor" if "Professor" in df.columns else "professor"
    col_local = "Local" if "Local" in df.columns else "local"
    col_horario = "Horário" if "Horário" in df.columns else ("horario" if "horario" in df.columns else "Horário / Sala")
    col_fase = "Fase" if "Fase" in df.columns else "fase"
    col_codigo = "Código da Disciplina" if "Código da Disciplina" in df.columns else ("Código" if "Código" in df.columns else "codigo_disciplina")
    col_nome = "Nome da Disciplina" if "Nome da Disciplina" in df.columns else "nome_disciplina"
    col_turma = "Turma" if "Turma" in df.columns else "turma"

    registros_expandidos = []

    for idx, row in df.iterrows():
        horario_str = row.get(col_horario, "")
        slots = parsear_horarios_detalhados(horario_str)
        
        prof = str(row.get(col_prof, "")).strip()
        local = str(row.get(col_local, "")).strip()
        fase = str(row.get(col_fase, "")).strip()
        codigo = str(row.get(col_codigo, "")).strip()
        nome = str(row.get(col_nome, "")).strip()
        turma = str(row.get(col_turma, "")).strip()

        for dia, hora in slots:
            registros_expandidos.append({
                "codigo": codigo,
                "nome": nome,
                "turma": turma,
                "professor": prof,
                "local": local,
                "fase": fase,
                "dia": dia,
                "hora": hora
            })

    df_exp = pd.DataFrame(registros_expandidos)
    if df_exp.empty:
        return conflitos_professor, conflitos_sala, conflitos_fase

    # ----------------------------------------------------
    # 1. AUDITORIA: CHOQUE DE PROFESSOR
    # ----------------------------------------------------
    # Termos provisórios/indefinidos que NÃO geram choque de professor
    profs_ignorados = [
        "", "A DEFINIR", "A DEFINIR / A DEFINIR", "NONE", "NAN", 
        "PROFESSOR A CONTRATAR", "A CONTRATAR", "PROFESSOR(A) A CONTRATAR"
    ]
    
    # Filtra apenas professores reais
    df_prof = df_exp[~df_exp["professor"].str.upper().isin(profs_ignorados)]
    # Também ignora se o nome do professor contiver 'A CONTRATAR' ou 'A DEFINIR'
    df_prof = df_prof[~df_prof["professor"].str.upper().str.contains("A CONTRATAR|A DEFINIR", na=False)]
    
    agrup_prof = df_prof.groupby(["professor", "dia", "hora"])

    for (prof, dia, hora), grupo in agrup_prof:
        if len(grupo) > 1:
            turmas_conflitantes = [f"{r['codigo']} (Turma {r['turma']})" for _, r in grupo.iterrows()]
            conflitos_professor.append({
                "professor": prof,
                "dia": dia,
                "hora": hora,
                "turmas": ", ".join(turmas_conflitantes),
                "detalhe": f"Professor(a) {prof} alocado(a) simultaneamente em: {', '.join(turmas_conflitantes)} na {dia} às {hora}."
            })

    # ----------------------------------------------------
    # 2. AUDITORIA: CHOQUE DE SALA / LOCAL
    # ----------------------------------------------------
    # Locais provisórios que NÃO geram choque de sala
    locais_ignorados = [
        "", "A DEFINIR", "A DEFINIR / A DEFINIR", "NONE", "NAN", "A DEFINIR /",
        "AUX-ALOCAR", "AUX ALOCAR", "ALOCAR", "SEMESTRE"
    ]
    
    df_sala = df_exp[~df_exp["local"].str.upper().isin(locais_ignorados)]
    # Também ignora se conter 'AUX-ALOCAR' ou 'A DEFINIR' no texto
    df_sala = df_sala[~df_sala["local"].str.upper().str.contains("AUX-ALOCAR|AUX ALOCAR|A DEFINIR|ALOCAR", na=False)]

    agrup_sala = df_sala.groupby(["local", "dia", "hora"])

    for (local, dia, hora), grupo in agrup_sala:
        if len(grupo) > 1:
            turmas_conflitantes = [f"{r['codigo']} (Turma {r['turma']})" for _, r in grupo.iterrows()]
            conflitos_sala.append({
                "local": local,
                "dia": dia,
                "hora": hora,
                "turmas": ", ".join(turmas_conflitantes),
                "detalhe": f"Sala/Espaço '{local}' alocado(a) simultaneamente para: {', '.join(turmas_conflitantes)} na {dia} às {hora}."
            })

    # ----------------------------------------------------
    # 3. AUDITORIA: CHOQUE DE HORÁRIO NA MESMA FASE
    # ----------------------------------------------------
    fases_regulares = ["1ª Fase", "2ª Fase", "3ª Fase", "4ª Fase", "5ª Fase", "6ª Fase"]
    df_fase = df_exp[df_exp["fase"].isin(fases_regulares)]
    agrup_fase = df_fase.groupby(["fase", "dia", "hora"])

    for (fase, dia, hora), grupo in agrup_fase:
        codigos_unicos = grupo["codigo"].unique()
        if len(codigos_unicos) > 1:
            disciplinas = [f"{r['codigo']} - {r['nome']} (T.{r['turma']})" for _, r in grupo.iterrows()]
            conflitos_fase.append({
                "fase": fase,
                "dia": dia,
                "hora": hora,
                "disciplinas": " vs ".join(disciplinas),
                "detalhe": f"Sobreposição na {fase} na {dia} às {hora}: {', '.join(disciplinas)}."
            })

    return conflitos_professor, conflitos_sala, conflitos_fase