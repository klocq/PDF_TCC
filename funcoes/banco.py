import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


def conectar_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def salvar_turmas_no_banco(df_dados: pd.DataFrame):
    if df_dados.empty:
        print("[Supabase] DataFrame vazio, nenhum dado para enviar.")
        return

    semestre_atual = df_dados["Semestre"].iloc[0]
    print(f"\n[Supabase] Limpando e enviando turmas do semestre {semestre_atual}...")

    try:
        supabase = conectar_supabase()

        # -------------------------------------------
        # 1. Limpa todas as turmas
        # -------------------------------------------
        # Ao deletar todas as linhas, o Trigger do Postgres detecta que
        # a tabela ficou vazia e reseta o ID para 1 automaticamente!
        supabase.table("turmas_ci").delete().neq("codigo_disciplina", "---").execute()

        # -------------------------------------------
        # 2. Prepara e insere os novos dados
        # -------------------------------------------
        lista_turmas = []
        for _, linha in df_dados.iterrows():
            turma_dict = {
                "codigo_disciplina": str(linha["Código da Disciplina"]).strip(),
                "turma": str(linha["Turma"]).strip(),
                "nome_disciplina": str(linha["Nome da Disciplina"]).strip(),
                "fase": str(linha["Fase"]).strip(),
                "tipo": str(linha["Tipo"]).strip(),
                "horas_aula": int(linha["Horas Aula"]),
                "ofertas": int(linha["Ofertas"]),
                "horario": str(linha["Horário"]).strip(),
                "local": str(linha["Local"]).strip(),
                "professor": str(linha["Professor"]).strip(),
                "semestre": str(linha["Semestre"]).strip()
            }
            lista_turmas.append(turma_dict)

        # Inserção limpa (começando do 1)
        resultado = supabase.table("turmas_ci").insert(lista_turmas).execute()

        print(f"[SUCESSO] {len(resultado.data)} turmas cadastradas a partir do ID 1!")

    except Exception as e:
        print(f"[ERRO] Falha ao salvar no Supabase: {e}")