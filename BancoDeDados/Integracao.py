from supabase import create_client, Client
import json
import os
from typing import List

# Definição direta (já que você quer fixar no código)
SUPABASE_URL = "https://mllulbtmniekwbjuwdje.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1sbHVsYnRtbmlla3dianV3ZGplIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc2OTUxMzAsImV4cCI6MjA3MzI3MTEzMH0.VZt-uJAe426e9dsNULNPio6ud5lOzxUlK3vNaLxjYuo"

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL ou SUPABASE_KEY ausentes.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def inserir_em_lotes(tabela: str, registros: List[dict], lote: int = 500):
    for i in range(0, len(registros), lote):
        parte = registros[i:i + lote]
        resp = supabase.table(tabela).insert(parte).execute()
        if not resp.data:
            print(f"Falha no lote {i // lote + 1}: {resp}")
            raise RuntimeError("Inserção interrompida.")
        else:
            print(f"Lote {i // lote + 1} inserido ({len(parte)} registros).")

def imprimir_exemplos_lista(dados: List[dict], n: int = 5):
    print(f"\n--- {min(n, len(dados))} exemplos do arquivo ---")
    for i, item in enumerate(dados[:n], start=1):
        print(f"\nExemplo {i}:")
        print(json.dumps(item, ensure_ascii=False, indent=2))

def imprimir_exemplos_bd(tabela: str, n: int = 5):
    try:
        resp = supabase.table(tabela).select("*").limit(n).execute()
        if resp.data:
            print(f"\n--- {len(resp.data)} exemplos do banco ---")
            for i, item in enumerate(resp.data, start=1):
                print(f"\nRegistro {i}:")
                print(json.dumps(item, ensure_ascii=False, indent=2))
        else:
            print("Tabela vazia para exemplos.")
    except Exception as e:
        print("Erro ao buscar exemplos do banco:", repr(e))

def inserir_json_no_supabase(caminho_arquivo: str, tabela: str):
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
        if not isinstance(dados, list):
            raise ValueError("JSON deve ser lista.")
        print(f"Total de registros a inserir: {len(dados)}")
        imprimir_exemplos_lista(dados, 5)  # imprime 5 antes de inserir
        inserir_em_lotes(tabela, dados)
        print("Inserção finalizada com sucesso.")
        imprimir_exemplos_bd(tabela, 5)    # imprime 5 após inserir
    except Exception as e:
        print("Erro ao processar/inserir:", repr(e))

def testar_tabela(tabela: str):
    try:
        resp = supabase.table(tabela).select("*").limit(1).execute()
        if resp.data:
            print("Tabela acessível. Exemplo:", resp.data[0])
        else:
            print("Tabela acessível (vazia).")
    except Exception as e:
        print("Erro ao acessar tabela:", repr(e))
    pass  # Para garantir que a função não faça nada em produção

# Ensure pytest does not collect this production function as a test
testar_tabela.__test__ = False

# (Opcional) Inserção direta via Postgres usando connection string
def inserir_via_postgres(caminho_arquivo: str, tabela: str):
    conn_str = os.environ.get("DATABASE_URL")  # ex: postgresql://postgres:SENHA@HOST:5432/postgres
    if not conn_str:
        print("DATABASE_URL não definida; pulando inserção direta.")
        return
    try:
        import psycopg2
        import psycopg2.extras
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
        if not isinstance(dados, list):
            raise ValueError("JSON deve ser lista.")
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()
        # Inserção simples (colunas JSON)
        for item in dados:
            cur.execute(
                f"""
                insert into "{tabela}"
                (tipo,endereco,quartos,banheiros,vagas_garagem,area_m2,preco_aluguel,descricao,
                 comodidades,fotos,avaliacoes,nota_media,regras_casa,camas,tipo_cama,politica_cancelamento,
                 anfitriao,wifi,checkin,checkout,ano_construcao,andar,condominio,iptu,mobiliado,
                 distancia_metro_km,distancia_onibus_km,max_hospedes,tempo_anuncio_meses,status,
                 latitude,longitude,tags,disponibilidade)
                values (
                  %(tipo)s,%(endereco)s,%(quartos)s,%(banheiros)s,%(vagas_garagem)s,%(area_m2)s,%(preco_aluguel)s,%(descricao)s,
                  %(comodidades)s,%(fotos)s,%(avaliacoes)s,%(nota_media)s,%(regras_casa)s,%(camas)s,%(tipo_cama)s,%(politica_cancelamento)s,
                  %(anfitriao)s,%(wifi)s,%(checkin)s,%(checkout)s,%(ano_construcao)s,%(andar)s,%(condominio)s,%(iptu)s,%(mobiliado)s,
                  %(distancia_metro_km)s,%(distancia_onibus_km)s,%(max_hospedes)s,%(tempo_anuncio_meses)s,%(status)s,
                  %(latitude)s,%(longitude)s,%(tags)s,%(disponibilidade)s
                )
                """,
                {
                    **item,
                    "endereco": json.dumps(item["endereco"]),
                    "comodidades": json.dumps(item["comodidades"]),
                    "fotos": json.dumps(item["fotos"]),
                    "avaliacoes": json.dumps(item["avaliacoes"]),
                    "regras_casa": json.dumps(item["regras_casa"]),
                    "anfitriao": json.dumps(item["anfitriao"]),
                    "tags": json.dumps(item["tags"]),
                    "disponibilidade": json.dumps(item["disponibilidade"])
                }
            )
        conn.commit()
        cur.close()
        conn.close()
        print("Inserção via Postgres finalizada.")
    except Exception as e:
        print("Erro inserção Postgres:", repr(e))

def obter_dados_tabela(tabela: str, colunas: str = "*", batch: int = 1000) -> list:
    """Busca todos os registros da tabela em lotes."""
    registros = []
    inicio = 0
    while True:
        fim = inicio + batch - 1
        resp = supabase.table(tabela).select(colunas).range(inicio, fim).execute()
        if not resp.data:
            break
        registros.extend(resp.data)
        if len(resp.data) < batch:
            break
        inicio += batch
    return registros

def salvar_tabela_para_json(tabela: str, caminho_saida: str, colunas: str = "*"):
    dados = obter_dados_tabela(tabela, colunas)
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"Exportados {len(dados)} registros para {caminho_saida}")

# Ajuste do main para somente ler a tabela
if __name__ == "__main__":
    tabela = "ImoveisDisponiveis"
    dados = obter_dados_tabela(tabela)
    print(f"Total de registros obtidos: {len(dados)}")
    print("\n--- 5 primeiros registros ---")
    for i, r in enumerate(dados[:5], start=1):
        print(f"\nRegistro {i}:")
        print(json.dumps(r, ensure_ascii=False, indent=2))
    # Opcional: salvar em JSON local
    # salvar_tabela_para_json(tabela, "dump_imoveis.json")