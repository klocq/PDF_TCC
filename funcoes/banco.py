import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

# Tenta carregar as variáveis locais (do arquivo .env, se existir no PC)
load_dotenv()

# -------------------------------------------
# FORMA SEGURA DE LER AS CHAVES (NUVEM VS LOCAL)
# -------------------------------------------
try:
    # 1. Tenta pegar da nuvem do Streamlit primeiro (Secrets)
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except (KeyError, FileNotFoundError):
    # 2. Se falhar (ex: rodando localmente sem Streamlit), tenta pegar do .env via OS
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Conexão global exportável para outros módulos usarem
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def conectar_supabase() -> Client:
    """Retorna a instância global do Supabase."""
    return supabase


def salvar_turmas_no_banco(df_dados: pd.DataFrame):
    if df_dados.empty:
        print("[Supabase] DataFrame vazio, nenhum dado para enviar.")
        return

    semestre_atual = df_dados["Semestre"].iloc[0]
    print(f"\n[Supabase] Limpando e enviando turmas do semestre {semestre_atual}...")

    try:
        # 1. Limpa todas as turmas
        supabase.table("turmas_ci").delete().neq("codigo_disciplina", "---").execute()

        # 2. Prepara e insere os novos dados (Removendo duplicatas visuais)
        df_banco = df_dados.drop_duplicates(subset=["Código da Disciplina", "Turma", "Semestre"], keep="first")

        lista_turmas = []
        for _, linha in df_banco.iterrows():
            turma_dict = {
                "codigo_disciplina": str(linha["Código da Disciplina"]).strip(),
                "turma": str(linha["Turma"]).strip(),
                "nome_disciplina": str(linha["Nome da Disciplina"]).strip(),
                "fase": str(linha["Fase"]).strip(),
                "tipo": str(linha["Tipo"]).strip(),
                "tipo_disciplina": str(linha.get("Tipo de Disciplina", "Específico")).strip(),
                "horas_aula": int(linha["Horas Aula"]),
                "ofertas": int(linha["Ofertas"]),
                "horario": str(linha["Horário"]).strip(),
                "local": str(linha["Local"]).strip(),
                "professor": str(linha["Professor"]).strip(),
                "semestre": str(linha["Semestre"]).strip()
            }
            lista_turmas.append(turma_dict)

        # Inserção limpa no Supabase
        resultado = supabase.table("turmas_ci").insert(lista_turmas).execute()
        print(f"[SUCESSO] {len(resultado.data)} turmas salvas no Supabase com sucesso!")

    except Exception as e:
        print(f"[ERRO] Falha ao salvar no Supabase: {e}")

# Adicione no final do arquivo banco.py

def obter_matriz_por_curriculo(curriculo_selecionado: str) -> pd.DataFrame:
    """Busca a matriz curricular no Supabase para o currículo selecionado ."""
    try:
        # Puxa os dados da tabela criada
        resposta = supabase.table("matriz_curricular").select("*").eq("curriculo", curriculo_selecionado).execute()
        
        # Converte para DataFrame do Pandas
        if resposta.data:
            return pd.DataFrame(resposta.data)
        return pd.DataFrame() # Retorna vazio se não achar nada
    except Exception as e:
        print(f"Erro ao buscar matriz no banco: {e}")
        return pd.DataFrame()