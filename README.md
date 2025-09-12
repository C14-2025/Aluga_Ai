
# Aluga_Ai - Consulta de API de estabelecimentos

=======
# Aluga_Ai


Projeto de geração, persistência e teste de dados simulados de imóveis para um cenário tipo marketplace (aluguel temporário / longa duração).

<<<<<<< Updated upstream
## Estrutura dos Arquivos
```bash
aluga_ai_web/
│
├── aluga_ai_web/ # Configuração principal do Django
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
│
├── reservas/ # App responsável pelas reservas
│ ├── views.py
│ ├── models.py
│ └── urls.py
│
├── API/ # Integrações externas
│ ├── ChamadaApi.py
│ ├── TesteApi.py
│ └── init.py
│
├── manage.py
```
- `API/ChamadaApi.py`: Funções para realizar a chamada à API e retornar o status HTTP.
- `API/TesteApi.py`: Teste automatizado usando pytest.
=======
## Principais Módulos

### 1. API de Geração de Dados
Arquivo: `API/ConstrucaoDeDados.py`  
Funções:
- `gerar_imovel()` cria um imóvel completo (endereço, anfitrião, comodidades, avaliações, disponibilidade etc.)
- `gerar_lista_imoveis(qtd)` retorna lista
- Execução direta gera e salva `imoveis_gerados.json`
>>>>>>> Stashed changes

Campos incluídos: localização (lat/long), regras, avaliações, tags, distâncias, status, política de cancelamento, mobiliado, custos (condomínio, IPTU), disponibilidade em períodos.

### 2. Integração com Supabase
Arquivo: `BancoDeDados/Integracao.py` (versão simplificada CRUD)  
Principais funções:
- `criar_imoveis(dados)`
- `listar_imoveis(limit, offset, ...)`
- `obter_imovel_por_id(id)`
- `atualizar_imovel(id, campos)`
- `deletar_imovel(id)`
- `deletar_todos_imoveis(confirmar=True)`

<<<<<<< Updated upstream
Certifique-se de ter o Python instalado. Para rodar o servidor e os testes, instale o pytest e o django:

```bash
pip install pytest django
=======
Arquivo de teste manual: `BancoDeDados/TesteCRUD.py`

Versão anterior (não ativa aqui) incluía inserção em lotes e exportação para JSON.

### 3. Testes Pytest

1. `API/TesteApi.py`  
   Testa:
   - Estrutura e campos obrigatórios.
   - Intervalos de valores (nota, área, latitude/longitude etc.).
   - Formato de avaliações, disponibilidade e tags.
   - Geração e escrita em arquivo temporário.

2. `BancoDeDados/testebd.py`  
   - Usa fakes (`FakeSupabase`) para simular o SDK.
   - Testa: inserção em lotes e exportação (pipeline `obter_dados_tabela` + `salvar_tabela_para_json`) do módulo alvo (ajuste de import conforme necessidade).

### 4. Arquivo JSON de Exemplo
`API/imoveis_gerados.json` contém um dataset extenso pronto para carga em banco (adequado à tabela `ImoveisDisponiveis` no Supabase).

## Estrutura Sugerida da Tabela (Supabase / Postgres)

```sql
create table public."ImoveisDisponiveis" (
  id serial primary key,
  tipo text,
  endereco jsonb,
  quartos int,
  banheiros int,
  vagas_garagem int,
  area_m2 int,
  preco_aluguel int,
  descricao text,
  comodidades jsonb,
  fotos jsonb,
  avaliacoes jsonb,
  nota_media float,
  regras_casa jsonb,
  camas int,
  tipo_cama text,
  politica_cancelamento text,
  anfitriao jsonb,
  wifi boolean,
  checkin text,
  checkout text,
  ano_construcao int,
  andar int,
  condominio int,
  iptu int,
  mobiliado boolean,
  distancia_metro_km float,
  distancia_onibus_km float,
  max_hospedes int,
  tempo_anuncio_meses int,
  status text,
  latitude float,
  longitude float,
  tags jsonb,
  disponibilidade jsonb
);
>>>>>>> Stashed changes
```

## Instalação

```bash
pip install pytest supabase psycopg2-binary
```

<<<<<<< Updated upstream
### 3. Rode o servidor

```bash
cd aluga_ai_web
python manage.py runserver
```
127.0.0.1:8000/consulta/ vai ser exibido os dados da API

### 4. Execute os testes
=======
(Se não usar Postgres direto, `psycopg2-binary` é opcional.)
>>>>>>> Stashed changes

## Execução da Geração

```bash
python API/ConstrucaoDeDados.py
```

Resultado: cria/atualiza `API/imoveis_gerados.json`

## Uso do CRUD (Supabase)

No arquivo `BancoDeDados/Integracao.py`, adapte ou mantenha as constantes:

```python
SUPABASE_URL = "https://SEU_PROJETO.supabase.co"
SUPABASE_KEY = "CHAVE_ANON_PUBLIC"
```

Depois:

```bash
python BancoDeDados/TesteCRUD.py
```

## Testes

Executar todos:

```bash
pytest
```

Executar somente geração:

```bash
pytest aluga_ai_web/API/TesteApi.py
```

<<<<<<< Updated upstream
## Observações
=======
## Boas Práticas

- Não deixe a `SUPABASE_KEY` (mesmo anon) em repositório público.
- Crie um `.env` (opcional) e carregue com `python-dotenv` se desejar.
- Para grandes volumes, implemente versão em lotes (já ilustrada em versões anteriores do módulo).
>>>>>>> Stashed changes

## Possíveis Extensões

- Filtro por cidade/bairro em `listar_imoveis`
- Indexação por geolocalização
- Endpoint FastAPI/Flask expondo CRUD
- Normalização parcial (separar anfitriões e avaliações)

## Problemas Comuns

| Sintoma | Causa | Solução |
|--------|-------|---------|
| 401 Invalid API key | Chave errada ou truncada | Copiar novamente de Settings > API |
| Campos ausentes em teste | Alteração em `gerar_imovel` | Atualizar lista de campos no teste |
| Falha de import pytest | Caminho relativo | Rodar na raiz do projeto `pytest` |

## Licença

Uso acadêmico / estudo. Ajustar conforme necessidade.

---
