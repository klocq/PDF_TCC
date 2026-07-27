import re
import pandas as pd

def executar_auditoria_data_quality(df):
    """
    Executa checagens de Data Quality em um DataFrame de turmas.
    Retorna um dicionário com métricas e alertas de integridade.
    """
    if df is None or df.empty:
        return {
            "status": "CRITICAL",
            "mensagem": "DataFrame vazio ou inválido.",
            "total_registros": 0,
            "metricas": {},
            "alertas": ["Nenhum dado foi fornecido para auditoria."]
        }

    total_registros = len(df)
    alertas = []
    
    # Identificação das colunas
    col_codigo = "Código da Disciplina" if "Código da Disciplina" in df.columns else ("Código" if "Código" in df.columns else "codigo_disciplina")
    col_horario = "Horário" if "Horário" in df.columns else "horario"
    col_prof = "Professor" if "Professor" in df.columns else "professor"
    col_local = "Local" if "Local" in df.columns else "local"
    col_turma = "Turma" if "Turma" in df.columns else "turma"

    # 1. Validação de Formato de Código (ex: CIN5101)
    padrao_codigo = re.compile(r'^[A-Z]{3}\d{4}$')
    codigos = df[col_codigo].astype(str).str.strip()
    codigos_invalidos = df[~codigos.str.match(padrao_codigo)]
    
    if not codigos_invalidos.empty:
        qtd_inv = len(codigos_invalidos)
        alertas.append(f"⚠️ {qtd_inv} registro(s) com formato de código fora do padrão (ex: {codigos_invalidos[col_codigo].iloc[0]}).")

    # 2. Validação de Formato de Horário UFSC (ex: 2.0820-2)
    padrao_horario = re.compile(r'\d\.\d{4}-\d')
    horarios = df[col_horario].astype(str)
    horarios_validos = horarios.apply(lambda x: bool(padrao_horario.search(x)))
    horarios_invalidos = df[~horarios_validos]

    if not horarios_invalidos.empty:
        qtd_h_inv = len(horarios_invalidos)
        alertas.append(f"⚠️ {qtd_h_inv} turma(s) sem horário padronizado no formato UFSC.")

    # 3. Métricas de Completude
    profs_provisorios = ["A DEFINIR", "PROFESSOR A CONTRATAR", "A CONTRATAR", "", "NAN", "NONE"]
    profs_definidos = df[~df[col_prof].astype(str).str.upper().isin(profs_provisorios)]
    pct_profs = (len(profs_definidos) / total_registros) * 100

    locais_provisorIOS = ["A DEFINIR", "AUX-ALOCAR", "ALOCAR", "SEMESTRE", "", "NAN", "NONE"]
    locais_definidos = df[~df[col_local].astype(str).str.upper().str.contains("AUX-ALOCAR|A DEFINIR|ALOCAR", na=False)]
    pct_locais = (len(locais_definidos) / total_registros) * 100

    # 4. Detecção de Duplicatas Absolutas (Código + Turma)
    duplicatas = df[df.duplicated(subset=[col_codigo, col_turma], keep=False)]
    if not duplicatas.empty:
        qtd_dup = len(duplicatas) // 2
        alertas.append(f"🔴 {qtd_dup} par(es) de turmas duplicadas encontradas no arquivo.")

    # Status geral de qualidade
    if len(alertas) == 0:
        status = "EXCELLENT"
        mensagem = "Dados 100% validados e dentro dos padrões de integridade!"
    elif any("🔴" in a for a in alertas):
        status = "WARNING"
        mensagem = "Dados processados com alertas críticos identificados."
    else:
        status = "GOOD"
        mensagem = "Dados processados com pequenas observações de preenchimento."

    relatorio = {
        "status": status,
        "mensagem": mensagem,
        "total_registros": total_registros,
        "metricas": {
            "pct_professores_definidos": round(pct_profs, 1),
            "pct_salas_definidas": round(pct_locais, 1),
            "pct_horarios_validos": round((sum(horarios_validos) / total_registros) * 100, 1)
        },
        "alertas": alertas
    }

    return relatorio