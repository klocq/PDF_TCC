import os
import re
import pypdf
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# 1. Disciplinas Exclusivas do Núcleo Específico de CI (5ª, 6ª fase e optativas do CIN)
ESPECIFICAS_EXCLUSIVAS_CI = {
    "CIN7601", "CIN7602", "CIN7603", "CIN7604", # 6ª Fase (Linked Data, Mídias Sociais, Empreendedorismo II, TCC)
    "CIN7501", "CIN7502", "CIN7503", "CIN7504", "CIN7505", # 5ª Fase (Mineração, Banco de Dados, Projetos, etc.)
    "CIN7903", "CIN7933", "CIN7938", "CIN7411", "MTM3687", "CIN7943", "CIN7907"
}


def extrair_codigos_disciplinas(caminho_pdf):
    """Extrai todos os códigos de disciplinas (ex: CIN5101) do PDF sem interrupções."""
    codigos = set()
    if not caminho_pdf or not os.path.exists(caminho_pdf):
        print(f"⚠️ Arquivo não encontrado: {caminho_pdf}")
        return codigos

    reader = pypdf.PdfReader(caminho_pdf)
    padrao_codigo = re.compile(r'[A-Z]{3}\d{4}')
    
    for page in reader.pages:
        texto = page.extract_text() or ""
        encontrados = padrao_codigo.findall(texto)
        codigos.update(encontrados)
        
    return codigos


def encontrar_pasta_entradas(base_dir):
    """Localiza a pasta de arquivos de entrada."""
    possiveis_pastas = ["arquivos_entrada", "entradas"]
    for pasta in possiveis_pastas:
        caminho = os.path.abspath(os.path.join(base_dir, "..", pasta))
        if os.path.exists(caminho):
            return caminho
    for pasta in possiveis_pastas:
        caminho = os.path.abspath(os.path.join(base_dir, pasta))
        if os.path.exists(caminho):
            return caminho
    return None


def repovoar_matriz():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pasta_entradas = encontrar_pasta_entradas(base_dir)
    
    if not pasta_entradas:
        print("❌ Pasta de arquivos de entrada não encontrada!")
        return

    # Caminhos dos PDFs
    pdf_ci_2026 = os.path.join(pasta_entradas, "CURRICULO_CIÊNCIA_DA_INFORMAÇÃO_20261.pdf (1).PDF")
    pdf_ci_2016 = os.path.join(pasta_entradas, "CURRICULO_CIÊNCIA_DA_INFORMAÇÃO_20161.pdf (3).PDF")
    pdf_arqui = os.path.join(pasta_entradas, "CURRICULO_ARQUIVOLOGIA_20161.pdf.PDF")
    pdf_biblio = os.path.join(pasta_entradas, "CURRICULO_BIBLIOTECONOMIA_(NOTURNO)_20161.pdf (3).PDF")

    print("🔎 Extraindo disciplinas dos 3 cursos...")
    
    # Extrai códigos de todos os PDFs
    codigos_ci = extrair_codigos_disciplinas(pdf_ci_2026) | extrair_codigos_disciplinas(pdf_ci_2016)
    codigos_arqui = extrair_codigos_disciplinas(pdf_arqui)
    codigos_biblio = extrair_codigos_disciplinas(pdf_biblio)

    print(f"\n📊 Resultado da Extração:")
    print(f"  • CI (Total): {len(codigos_ci)} disciplinas identificadas")
    print(f"  • Arquivologia: {len(codigos_arqui)} disciplinas identificadas")
    print(f"  • Biblioteconomia: {len(codigos_biblio)} disciplinas identificadas")

    if not codigos_ci:
        print("❌ Nenhum código encontrado para Ciência da Informação. Verifique se os arquivos estão na pasta entradas/.")
        return

    registros = []
    qtd_comum = 0
    qtd_especifico = 0

    for codigo in codigos_ci:
        em_arqui = codigo in codigos_arqui
        em_biblio = codigo in codigos_biblio

        # Regra de classificação:
        # Se estiver na lista garantida de exclusivas do CIN -> Específico
        if codigo in ESPECIFICAS_EXCLUSIVAS_CI:
            tipo_nucleo = "Específico"
        else:
            # Se for compartilhada com Arqui ou Biblio -> Comum, senão -> Específico
            tipo_nucleo = "Comum" if (em_arqui or em_biblio) else "Específico"

        if tipo_nucleo == "Comum":
            qtd_comum += 1
        else:
            qtd_especifico += 1

        registros.append({
            "codigo": codigo,
            "tipo_nucleo": tipo_nucleo,
            "pertence_arqui": em_arqui,
            "pertence_biblio": em_biblio
        })

    print(f"\n📈 Classificação Mapeada:")
    print(f"  • Disciplinas Núcleo Comum: {qtd_comum}")
    print(f"  • Disciplinas Núcleo Específico: {qtd_especifico}")

    print(f"\n🔄 Atualizando o Supabase...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Atualiza no Supabase
    supabase.table("disciplinas_matriz").upsert(registros).execute()
    print("✅ Tabela 'disciplinas_matriz' atualizada com sucesso no Supabase!")


if __name__ == "__main__":
    repovoar_matriz()