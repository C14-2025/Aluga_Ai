<p align="center">
   <img src="https://img.shields.io/badge/status-em%20desenvolvimento-yellow" alt="status" />
   <img src="https://img.shields.io/badge/python-3.13-blue" alt="python" />
   <img src="https://img.shields.io/badge/django-%20-green" alt="django" />
</p>

# Aluga_Ai

Plataforma acadêmica que simula um marketplace de aluguel de imóveis (temporário e longa duração) com:
- Geração e enriquecimento de dados de propriedades (scripts ETL)
- Persistência / CRUD (Supabase simplificado)
- Sistema de recomendação pessoal (ativado após favoritos) + validação por script
- Testes automatizados (pytest / Django test runner)
- Pipeline CI/CD em Jenkins (stages para validação e testes de recomendação)
- Containerização (Docker)

Inclui também integração com API externa (exemplo inicial) e estrutura expansível para novas features.

## O que tem no projeto (resumo)

- App Django completo (propriedades, usuários, reservas, recomendações) com templates e static.
- ETL e geração de dados sintéticos, além de scripts de validação do sistema de recomendação.
- Testes automatizados com pytest e runner nativo Django.
- CI/CD com Jenkins via Docker Compose, plugins pré-instalados e configuração por código (JCasC).
- Compose para subir app e Jenkins em contêineres separados.

## 1. Estrutura do Projeto

```bash
ALUGA_AI/

 aluga_ai_web/                  # Diretório raiz interno do projeto Django
    aluga_ai_web/              # Configurações Django (settings, urls, wsgi, asgi)
    BancoDeDados/              # Integração CRUD + testes BD (`test_bd.py`)
    Dados/                     # ETL, geração de dados, testes (`test_etl.py`)
    ml/                        # Treino e modelos (ex: `train_model.py`, `models/model.pkl`)
    reservas/ / usuarios/ ...  # Apps Django (ex: reservas, usuários, propriedades)
    jobs/                      # Scripts auxiliares (ex: `validate_recommendation_system.py`)
 Jenkinsfile                    # Pipeline Jenkins declarativa parametrizada
 Como_usar.md                   # Guia rápido para rodar app e pipeline
 docker-compose.yml             # Orquestração local (Jenkins + app)
 Dockerfile                     # Container da aplicação Django
 requirements.txt               # Dependências Python
 manage.py                      # Entrypoint Django
 validation_results.json        # Saída da validação do sistema de recomendação
```

### Modelagem de Dados (resumo)
Campos gerados incluem: localização (lat/long), regras, avaliações, tags, distâncias, status, política de cancelamento, mobiliado, custos (condomínio/IPTU), disponibilidade por período, atributos para recomendação.

## 2. Integração & Persistência
Arquivo principal: `BancoDeDados/Integracao.py`
Funções básicas CRUD:
```python
criar_imoveis(dados)
listar_imoveis(limit, offset, filtros)
obter_imovel_por_id(id)
atualizar_imovel(id, campos)
deletar_imovel(id)
deletar_todos_imoveis(confirmar=True)
```

## 3. Execução Local Rápida
Pré-requisitos: Python 3.13
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000
```
Acesse: <http://localhost:8000>

## 3.1. Execução completa com Docker Compose (recomendado)
Pré-requisitos: Docker Desktop + Git

1. Clonar o repositório e preparar variáveis de ambiente

```powershell
git clone <URL_DO_REPO>
cd Aluga_Ai
Copy-Item .env.example .env   # Edite se quiser trocar usuário/senha admin do Jenkins
```

1. Subir Jenkins e a aplicação (primeira vez pode demorar pelos plugins do Jenkins)

```powershell
docker compose up -d --build jenkins app
```

1. URLs e credenciais

- App (Django): <http://localhost:8000>
- Jenkins: <http://localhost:8080>
- Login Jenkins (padrão vindo do .env):
   - usuário: admin
   - senha: admin123
   - Altere a senha após o primeiro login.

1. O que o Jenkins já provisiona automaticamente

- Plugins a partir de `jenkins-plugins.txt`.
- Configuração por código (`jenkins-casc.yaml`), incluindo usuário admin.
- Um job Pipeline chamado `Aluga_Ai_Pipeline` (Job DSL) que roda sobre o diretório montado `/workspace` (código do repo). Basta clicar em “Build Now”.

1. Parar os serviços

```powershell
docker compose down
```

## 4. Testes
Rodar todos:
```powershell
pytest -v
```
Testes específicos:
```powershell
pytest aluga_ai_web/BancoDeDados/test_bd.py
pytest aluga_ai_web/Dados/test_etl.py
python manage.py test
```

## 5. ETL & Geração de Dados
Script principal: `aluga_ai_web/Dados/etl.py` (pipeline de transformação). Executar:
```powershell
venv\Scripts\activate
python aluga_ai_web/Dados/etl.py
```
Geração de dados simulados: `ConstrucaoDeDados.py`

## 6. Sistema de Recomendação

### Fluxo de uso na interface

1. Usuário navega pelos imóveis utilizando filtros simples (cidade, bairro, tipo, área, preço, amenidades). Estes filtros NÃO disparam recomendações – apenas refinam a lista principal.
2. Ao favoritar imóveis (botão ☆ / ★), o sistema calcula recomendações pessoais e as persiste em `UserRecommendation`.
3. A aba "Recomendados" surge e exibe até 6 imóveis sugeridos (score + preço estimado).
4. Remover favoritos recalcula o conjunto; se não houver favoritos suficientes, a aba mostra aviso.

### Validação via script (checagem rápida)

```powershell
venv\Scripts\activate
python jobs/validate_recommendation_system.py
```
"""
Aluga_Ai
============

Projeto acadêmico que simula um marketplace de aluguel de imóveis (curta e longa duração).

Este README serve como guia prático para configurar, rodar e contribuir com o projeto.

Estrutura resumida
------------------
- `manage.py` — entrypoint do Django
- `aluga_ai_web/` — configurações Django
- `recomendacoes/` — sistema de recomendação + scripts de validação
- `dados/` — ETL e diretório de relatórios (`dados/reports` usado em CI)
- `Jenkinsfile` — pipeline Declarative Jenkins
- `Dockerfile`, `docker-compose.yml` — containerização
- `requirements.txt` — dependências Python

Pré-requisitos
--------------
- Python 3.11+ (Python 3.13 recomendado para desenvolvimento)
- Git
- (Opcional) Docker Desktop + Docker Compose

Execução local (PowerShell)
---------------------------
1) Criar e ativar virtualenv:

```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
```

2) Instalar dependências:

```powershell
pip install -r requirements.txt
```

3) Aplicar migrações e criar superusuário (opcional):

```powershell
python manage.py migrate --noinput
python manage.py createsuperuser
```

4) Rodar servidor de desenvolvimento:

```powershell
python manage.py runserver 0.0.0.0:8000
```

Abra `http://localhost:8000`.

Execução com Docker Compose (Jenkins + app)
-----------------------------------------
```powershell
Copy-Item .env.example .env
docker compose up -d --build jenkins app
```

- App: http://localhost:8000
- Jenkins: http://localhost:8080 (credenciais via JCasC, ver `.env.example`)

Parar:

```powershell
docker compose down
```

Testes e validação
------------------
- Todos os testes com `pytest`:

```powershell
pytest -v
```

- Testes Django nativos:

```powershell
python manage.py test
```

- Teste de recomendação pessoal (exemplo):

```powershell
pytest recomendacoes/Testes/Teste_recomendacao.py -q
```

- Script de validação do sistema de recomendação:

```powershell
python recomendacoes/Testes/ValidacaoSistema.py
```

O script gera `validation_results.json` no diretório do projeto. Em CI a pipeline costuma mover esse arquivo para `dados/reports/` e arquivá-lo.

CI / Jenkins
------------
O repositório inclui um `Jenkinsfile` com stages para:
- instalar dependências
- rodar ETL e testes
- gerar relatórios (pytest HTML/JUnit)
- executar a validação do sistema de recomendação e arquivar `validation_results.json`

Se usar o `docker-compose`, o serviço `jenkins` provisiona plugins listados em `jenkins-plugins.txt` e aplica configuração via `jenkins-casc.yaml`.

Dicas rápidas / Troubleshooting
------------------------------
- Arquivos estáticos não aparecendo? Verifique `aluga_ai_web/settings.py` e execute `python manage.py collectstatic`.
- Erro Docker `COPY stack/`? Confirme se a pasta `stack/` existe ou remova a linha no `Dockerfile`.
- Erro Docker/WSL (rpc error / EOF)? Reinicie Docker Desktop e rode `wsl --shutdown`.

Contribuição
------------
1. Crie uma branch: `git checkout -b feature/minha-feature`
2. Implemente e adicione testes
3. Commit & push
4. Abra PR para `main`

Arquivos importantes modificados recentemente
--------------------------------------------
- `Jenkinsfile` — atualizações para ETL, geração de relatórios e arquivamento de `validation_results.json`.
- `recomendacoes/Testes/ValidacaoSistema.py` — versão com modo mock usada em CI para validação determinística.
- `aluga_ai_web/settings.py` — ajuste `STATIC_ROOT` para coleta de arquivos estáticos.

Próximos passos disponíveis
--------------------------
- Posso commitar essas mudanças e abrir um PR. Deseja que eu faça isso?

"""
| Job pipeline não aparece | Plugins ausentes | Reinstalar plugins, reiniciar Jenkins. |
