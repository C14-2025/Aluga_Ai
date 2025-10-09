# Aluga_Ai - Sistema de Reservas de Imóveis

Sistema completo de marketplace para aluguel de imóveis temporários, desenvolvido com Django REST Framework. Inclui funcionalidades de busca, reserva, avaliação e gerenciamento de imóveis.

## 🚀 Funcionalidades

- **Sistema de Imóveis**: Cadastro e gerenciamento de imóveis com filtros avançados
- **Sistema de Reservas**: Criação, confirmação e cancelamento de reservas
- **Sistema de Avaliações**: Avaliação de imóveis e hóspedes
- **Autenticação JWT**: Sistema seguro de autenticação
- **API REST Completa**: Endpoints para todas as operações
- **Filtros e Busca**: Busca por localização, preço, comodidades e disponibilidade
- **Validações de Negócio**: Regras para reservas, cancelamentos e avaliações

## 📁 Estrutura do Projeto

```bash
ALUGA_AI/
├── aluga_ai_web/                 # Projeto Django principal
│   ├── aluga_ai_web/             # Configurações Django
│   │   ├── settings.py           # Configurações do projeto
│   │   ├── urls.py               # URLs principais
│   │   └── wsgi.py               # WSGI configuration
│   ├── usuarios/                  # App de usuários
│   │   ├── models.py             # Modelos de usuário
│   │   ├── views.py              # Views de autenticação
│   │   └── serializers.py        # Serializers de usuário
│   ├── reservas/                 # App de reservas (PRINCIPAL)
│   │   ├── models.py             # Modelos: Imovel, Reserva, Avaliacao
│   │   ├── views.py              # ViewSets para API REST
│   │   ├── serializers.py        # Serializers para validação
│   │   ├── urls.py               # URLs das reservas
│   │   └── tests.py              # Testes automatizados
│   ├── BancoDeDados/             # Integração com Supabase
│   │   ├── Integracao.py         # CRUD operations
│   │   └── test_bd.py            # Testes de integração
│   ├── Dados/                    # Geração de dados
│   │   ├── ConstrucaoDeDados.py  # Gerador de dados simulados
│   │   ├── imoveis_gerados.json  # Dados gerados
│   │   └── test_api.py           # Testes de geração
│   ├── manage.py                 # Comando Django
│   ├── populate_data.py          # Script para popular banco
│   └── API_DOCUMENTATION.md     # Documentação da API
├── requirements.txt              # Dependências Python
├── pytest.ini                   # Configurações pytest
└── README.md                     # Este arquivo
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

---
