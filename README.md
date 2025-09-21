<<<<<<< Updated upstream

# Aluga_Ai - Consulta de API de estabelecimentos

=======
# Aluga_Ai


Projeto de geração, persistência e teste de dados simulados de imóveis para um cenário tipo marketplace (aluguel temporário / longa duração).
=======
# Aluga_Ai - Consulta de API de Estabelecimentos

Este projeto realiza chamadas à [Realtor API Data](https://rapidapi.com/) para obter detalhes de escolas utilizando Python e Django. Inclui testes automatizados com pytest para garantir o funcionamento das requisições.
>>>>>>> Stashed changes

## Estrutura dos Arquivos

```bash
ALUGA_AI/
│
<<<<<<< Updated upstream
├── .pytest_cache/
│
├── aluga_ai_web/                 # Pasta principal do projeto
│   │
│   ├── aluga_ai_web/             # Diretório Django principal (settings, urls, wsgi, etc.)
│   │
│   ├── BancoDeDados/ 
│   │   └── test_bd.py              # Arquivo de testes (pytest)
│   │
│   ├── Dados/                    # Scripts, geradores de dados e testes unitários relacionados
│   │   └── test_api.py           # Arquivo de testes (pytest)
│   │
│   └── reservas/                 # Aplicação Django para gerenciamento de reservas
│
├── .gitignore                    # Arquivos/pastas ignorados pelo Git
├── manage.py                     # Comando principal para rodar o Django
├── pytest.ini                    # Configurações do pytest-django
├── README.md                     # Documentação do projeto
└── requirements.txt              # Dependências do Python
=======
├── aluga_ai_web/           # Configuração principal do Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── reservas/               # App responsável pelas reservas
│   ├── views.py
│   ├── models.py
│   └── urls.py
│
├── API/                    # Integrações externas
│   ├── ChamadaApi.py       # Funções para chamada à API
│   ├── TesteApi.py         # Testes automatizados (pytest)
│   └── __init__.py
│
├── manage.py
>>>>>>> Stashed changes
```

<<<<<<< Updated upstream
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
=======
## Configuração

1. **Instale as dependências**
>>>>>>> Stashed changes

   Certifique-se de ter o Python instalado. Para rodar o servidor e os testes, instale o pytest e o Django:

   ```bash
   pip install pytest django requests
   ```

<<<<<<< Updated upstream
## Instalação

```bash
pip install pytest supabase psycopg2-binary
```
=======
2. **Configure sua chave da API**

   - Obtenha uma chave de API no [RapidAPI](https://rapidapi.com/).
   - Adicione sua chave em `API/ChamadaApi.py` conforme instruções no próprio arquivo.
>>>>>>> Stashed changes

3. **Realize a chamada à API**

   Você pode importar e usar a função `chamada_api()` para obter os dados da escola em formato JSON (string).

4. **Rode o servidor Django**

<<<<<<< Updated upstream
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
pytest -v
```

Executar somente geração:

```bash
pytest .\aluga_ai_web\Dados\test_api.py
```

Executar somente integração:

```bash
pytest .\aluga_ai_web\BancoDeDados\test_bd.py
```

## Observações

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
=======
   ```bash
   cd aluga_ai_web
   python manage.py runserver
   ```
   Acesse `http://127.0.0.1:8000/consulta/` para visualizar os dados da API.

5. **Execute os testes**

   Para rodar o teste automatizado e verificar se a API está respondendo corretamente:

   ```bash
   pytest aluga_ai_web/API/TesteApi.py
   ```

## Observações

- O projeto utiliza uma chave de API do RapidAPI. **Não exponha sua chave em ambientes públicos.**
- O endpoint utilizado consulta detalhes de uma escola específica (`id=0717323601`).
- Os testes automatizados garantem que a resposta da API está correta.
>>>>>>> Stashed changes

---
