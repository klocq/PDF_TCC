import re
import pandas as pd

# ____________________________________________________
# 1 - O que faz?
# ----------------------------------------------------
# Processa o texto bruto extraído do PDF via Expressões 
# Regulares, identificando turmas, horários, locais e 
# professores, tratando linhas órfãs e cabeçalhos.
# ____________________________________________________
def processar_texto_bruto(texto_bruto):
    dados_estruturados = []
    linhas = texto_bruto.split("\n")

    padrao_inicio = re.compile(r'^([A-Z]{3}\d{4})\s+(\d{5}[A-Z]?)')
    padrao_horario_ufsc = re.compile(r'(\d\.\d{4}-\d\s*/\s*[A-Z0-9-]+(?:\s+[A-Z]\b)?)')

    palavras_proibidas_professor = {
        "VAGAS", "OFERTADAS", "OCUPADAS", "ALUNOS", "ESPECIAIS", "SALDO",
        "PEDIDOS", "SEM", "VAGA", "PROFESSORES", "CURSO", "DISCIPLINA", "NOME"
    }

    linha_acumulada = ""

    for linha in linhas:
        linha = linha.strip()

        if not linha:
            continue

        # 1. Filtro de cabeçalhos do documento
        linha_maiuscula = linha.upper()
        if ("SEMESTRE:" in linha_maiuscula or
            "CADASTRO DE TURMAS" in linha_maiuscula or
            "SETIC" in linha_maiuscula or
            "PÁGINA:" in linha_maiuscula):
            continue

        # 2. Tratamento de linhas órfãs
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

        # 3. Processamento da linha principal da disciplina
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

    # Devolvemos apenas os dados limpos extraídos.
    return dados_estruturados