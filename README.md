<p align="center">
   <img src="https://img.shields.io/badge/status-em%20desenvolvimento-yellow" alt="status" />
   <img src="https://img.shields.io/badge/python-3.13-blue" alt="python" />
   <img src="https://img.shields.io/badge/django-%20-green" alt="django" />
</p>

# Aluga_Ai

Plataforma acadêmica que simula um marketplace de aluguel de imóveis (temporário e longa duração) com:
- Geração e enriquecimento de dados de propriedades (scripts ETL)
- Persistência / CRUD (Supabase simplificado)
- Sistema de recomendação validado por script de análise
- Testes automatizados (pytest / Django test runner)
- Pipeline CI/CD parametrizada em Jenkins
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
Validação rápida:
```powershell
venv\Scripts\activate
python jobs/validate_recommendation_system.py
```
Resultados consolidados em `validation_results.json`.

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
Pipeline declarativa em `Jenkinsfile` com parâmetros:
| Param | Default | Descrição |
|-------|---------|-----------|
| RUN_TESTS | true | Executa estágios de teste/qualidade/validação. |
| BUILD_DOCKER_IMAGE | false | Constrói imagem Docker. |
| PUSH_TO_REGISTRY | false | Faz push da imagem para Docker Hub. |
| DEPLOY_APP | false | Deploy (somente branch `main`). |
| DOCKERHUB_REPO | `seu-usuario/aluga-ai` | Repositório Docker destino. |
| CREDENTIALS_ID | `dockerhub-credentials` | ID de credencial Jenkins para login. |
| NOTIFY_EMAIL | (vazio) | E-mail para notificações de sucesso/falha. |

Fluxo condicional:
1. Checkout / Prepare sempre.
2. Testes + Qualidade se `RUN_TESTS`.
3. Build se `BUILD_DOCKER_IMAGE`.
4. Push se Build + `PUSH_TO_REGISTRY`.
5. Deploy se Build + Push + `DEPLOY_APP` + branch `main`.

Relatórios: HTML (pytest), artefatos (`pylint_report.txt`, `flake8_report.txt`, `server.log`).
Guia de uso completo (Jenkins, webhook, Docker Hub): ver `Como_usar.md`.

### 8.1. Jenkins via Docker Compose (detalhes)
- Serviço `jenkins` definido em `docker-compose.yml` com volume nomeado `jenkins_home` que persiste tudo (usuários, jobs, histórico, credenciais).
- `Dockerfile.jenkins` instala plugins por `jenkins-plugin-cli` e copia `jenkins-casc.yaml` (JCasC) para configuração automática.
- Credenciais admin do Jenkins vêm do `.env` (não commitar `.env`, use `.env.example`).
- Se quiser um reset completo do Jenkins (opcional), remova o volume e suba novamente:
   ```powershell
   docker compose down
   docker volume rm aluga_ai_jenkins_home
   docker compose up -d --build jenkins
   ```
   ATENÇÃO: isso apaga jobs/usuários/histórico do Jenkins. Faça backup antes se necessário.

### 8.2. Atualizando a imagem / mudanças recentes
- Após editar `Dockerfile.jenkins`, `jenkins-plugins.txt` ou `jenkins-casc.yaml`:
   ```powershell
   docker compose build jenkins
   docker compose up -d jenkins
   ```
- Em Jenkins JÁ inicializado (volume existente), novos plugins podem precisar ser instalados no volume e Jenkins reiniciado:
   ```powershell
   docker exec jenkins-aluga-ai jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt --verbose
   docker restart jenkins-aluga-ai
   ```

### 8.3. Disparo automático por Git (opcional)
- O job `Aluga_Ai_Pipeline` default usa script inline e não dispara em commits.
- Para builds automáticos por commit, crie um Pipeline “from SCM” ou Multibranch apontando para seu repositório e configure:
   - Webhook (recomendado) OU
   - Poll SCM (cron), por exemplo `H/5 * * * *`.

### Cenários
| Objetivo | Configuração |
|----------|--------------|
| Somente testes | RUN_TESTS=true; demais false |
| Build local | RUN_TESTS=true; BUILD_DOCKER_IMAGE=true |
| Publicar imagem | RUN_TESTS=true; BUILD_DOCKER_IMAGE=true; PUSH_TO_REGISTRY=true |
| Deploy produção | (branch main) todos true |

### Criação Multibranch
1. New Item  Multibranch Pipeline
2. Git URL do repositório
3. Scan Repository
4. Executar branch `Actions_to_Jenkins`

## 9. Branches
- `main`: linha principal / produção
- `Actions_to_Jenkins`: migração CI/CD
- Futuras feature branches: integração automática via multibranch

## 10. Qualidade de Código
Ferramentas: `pylint`, `flake8` (não bloqueiam build: `--exit-zero`).
Possível expansão: adicionar cobertura (`coverage.py`) e métricas.

## 11. Troubleshooting Rápido
| Sintoma | Causa | Solução |
|--------|-------|---------|
| Erro venv no Jenkins | Ambiente limpo sem Python global | Jenkinsfile já cria venv; garantir imagem base padrão. |
| Plugin HTML não publica | Plugin ausente | Instalar "HTML Publisher" no Jenkins. |
| Push Docker falha | Credenciais inválidas | Recriar credencial `dockerhub-credentials`. |
| Deploy ignorado | Branch diferente de main | Fazer merge para `main`. |
| Teste ETL falha | Mudança em schema | Atualizar testes e scripts de geração. |
| Não consigo logar no Jenkins (pede password inicial) | Novo volume na sua máquina | Use admin/senha do `.env` (JCasC) — não é o `initialAdminPassword`. |
| Jenkins não mostra o job | Plugins JCasC/Job DSL não instalados ainda | Rode o comando de plugin-cli acima e reinicie Jenkins. |
| Porta 8080/8000 em uso | Outro serviço usando a porta | Feche o serviço conflitando ou mude portas no compose. |

## 12. Próximas Extensões
- Cobertura de testes (coverage + badge)
- Geração de imagem multi-stage (menor tamanho)
- Webhooks para builds automáticos em cada push
- Testes de integração + carga
- Observabilidade (logging estruturado / métricas)

## 13. Contribuição
1. Criar branch feature
2. Implementar + testes
3. Commit + push
4. Abrir PR para `main`
5. Esperar validação da pipeline e revisão

## 14. Licença / Uso
Uso acadêmico e estudo. Ajuste conforme necessidade institucional.

## 15. Contato / Suporte
Em caso de dúvidas: abrir Issue ou contatar responsáveis da turma.

---
_Este README foi atualizado para refletir a migração de GitHub Actions para Jenkins e a adoção de uma pipeline parametrizada com suporte a Docker e deploy._
Os testes automatizados garantem que a resposta da API está correta.
