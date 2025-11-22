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

Saída: `validation_results.json` (arquivos, carregamento de modelo, predição, recomendação).

### Teste automatizado de recomendação pessoal

```powershell
pytest recomendacoes/tests/test_personal_recommend.py -q
```

Cobertura: criação de usuário, favoritos iniciais, endpoint `/api/ml/personal_recommend/`, exclusão dos favoritos nas recomendações e persistência em `UserRecommendation`.

## 7. Containerização

Dockerfile simplificado:

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

Build & run:

```powershell
docker build -t aluga-ai:dev .
docker run -it --rm -p 8000:8000 aluga-ai:dev
```

Parar:

```powershell
docker stop $(docker ps -q --filter ancestor=aluga-ai:dev)
```

Ou via Docker Compose:

```powershell
docker-compose up -d app
docker-compose down
```

## 8. CI/CD (Jenkins)

Pipeline declarativa em `Jenkinsfile` com parâmetros atuais:

| Param | Default | Descrição |
|-------|---------|-----------|
| NOTIFY_EMAIL | (vazio) | Email para notificação de sucesso/falha. |
| DOCKERHUB_REPO | `alvarocareli/aluga-ai` | Repositório Docker Hub destino. |

### Stages principais

- Checkout / Prepare (define tag da imagem)
- Setup Python / Install Dependencies / Migrations
- Testes Banco de Dados (`BancoDeDados/test_bd.py`)
- Testes API / ETL (`Dados/test_etl.py` + execução `etl.py`)
- Testes Propriedades & Reservas
- Validação Recomendação (script `jobs/validate_recommendation_system.py`)
- Testes Django gerais (`manage.py test`)
- Code Quality (`pylint`, `flake8`)
- Teste de subida de servidor (`runserver` + curl)
- Testes Recomendação Personalizada (`recomendacoes/tests/test_personal_recommend.py`)
- Deploy (somente branch `main`)

Relatórios/artefatos: HTML pytest, `validation_results.json`, logs server, lint reports.

Adicionar novos testes: criar arquivos `test_*.py` em `recomendacoes/tests/`.

### 8.1. Jenkins via Docker Compose (detalhes)

Serviço `jenkins` em `docker-compose.yml` com volume `jenkins_home` (persiste usuários, jobs, histórico, credenciais).
`Dockerfile.jenkins` instala plugins via `jenkins-plugin-cli` e aplica `jenkins-casc.yaml` (JCasC).
Credenciais admin vêm do `.env` (não commitar `.env`, use `.env.example`).
Reset completo (apaga tudo):

```powershell
docker compose down
docker volume rm aluga_ai_jenkins_home
docker compose up -d --build jenkins
```

ATENÇÃO: apaga jobs/usuários/histórico; faça backup antes.

### 8.2. Atualizando a imagem / mudanças recentes

Após editar `Dockerfile.jenkins`, `jenkins-plugins.txt` ou `jenkins-casc.yaml`:

```powershell
docker compose build jenkins
docker compose up -d jenkins
```

Em Jenkins já inicializado (volume existente), reinstalar plugins e reiniciar:

```powershell
docker exec jenkins-aluga-ai jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt --verbose
docker restart jenkins-aluga-ai
```

### 8.3. Disparo automático por Git (opcional)

Job padrão usa script inline e não dispara em commits.
Para builds automáticos: criar Pipeline "from SCM" ou Multibranch e configurar:

- Webhook (recomendado) OU
- Poll SCM (`H/5 * * * *`).

### Multibranch (opcional)

Criar um job Multibranch apontando para o repositório para builds automáticos por branch/PR (webhook ou polling).

## 9. Branches

`main` (produção), `Ajustes-IntegraçaoIA` (recomendações / integração recente) e futuras feature branches (multibranch opcional).

## 10. Qualidade de Código

Ferramentas: `pylint`, `flake8` (não bloqueiam build: `--exit-zero`). Expansão planejada: cobertura (`coverage.py`), métricas de complexidade, duplicação.

## 11. Troubleshooting Rápido

| Sintoma | Causa | Solução |
|--------|-------|---------|
| Erro venv no Jenkins | Ambiente limpo | Jenkinsfile cria venv; checar Python base. |
| HTML report não publica | Plugin ausente | Instalar "HTML Publisher". |
| Push Docker falha | Credencial incorreta | Recriar `dockerhub-credentials`. |
| Deploy ignorado | Branch ≠ main | Fazer merge para `main`. |
| Teste ETL falha | Schema mudou | Ajustar script e teste. |
| Login Jenkins pede senha inicial | Volume novo | Usar admin/senha do `.env` (JCasC). |
| Job pipeline não aparece | Plugins ausentes | Reinstalar plugins, reiniciar Jenkins. |
| Portas ocupadas | Conflito local | Alterar portas ou parar serviço. |

## 12. Próximas Extensões

- Cobertura de testes e badge
- Multi-stage Docker para reduzir imagem
- Webhooks Git para disparo automático
- Testes de integração e carga
- Observabilidade (logs estruturados / métricas / tracing)

## 13. Contribuição

1. Criar branch feature
2. Implementar + testes
3. Commit + push
4. Abrir PR para `main`
5. Aguardar pipeline e revisão

## 14. Licença / Uso

Uso acadêmico e estudo. Ajuste conforme necessidade institucional.

## 15. Contato / Suporte

Em caso de dúvidas: abrir Issue ou contatar responsáveis da turma.

---
_README atualizado: fluxo de recomendação pessoal, nova organização de testes e ajustes no Jenkinsfile._
Os testes automatizados garantem funcionamento de CRUD, ETL e recomendações pessoais.
