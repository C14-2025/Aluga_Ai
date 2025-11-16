# Guia da Pipeline e Execução do Projeto Aluga_Ai

> Objetivo: Ensinar rapidamente como rodar o projeto localmente e como usar a pipeline do Jenkins com seus parâmetros de controle.

---
## 1. Pré-requisitos

### Local (sem Docker)
- Python 3.13 instalado
- Pip disponível em PATH

### Docker (opcional)
- Docker Desktop instalado (Windows)

### Jenkins
- Container Jenkins rodando em `http://localhost:8080` (já levantado via `docker-compose`)
- Volume `jenkins_home` preserva configurações

---
## 2. Clonar o Repositório
```powershell
git clone https://github.com/C14-2025/Aluga_Ai.git
cd Aluga_Ai
# Verifique branch de migração
git checkout Actions_to_Jenkins
```

---
## 3. Executar Localmente (sem Docker)
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000
```
Acesse: http://localhost:8000

### Rodar Testes
```powershell
venv\Scripts\activate
pytest aluga_ai_web/BancoDeDados/test_bd.py
pytest aluga_ai_web/Dados/test_etl.py
python manage.py test
```

---
## 4. Executar com Docker (aplicação)
```powershell
docker build -t aluga-ai-local:dev -f Dockerfile .
docker run -d --name aluga-ai --restart unless-stopped -p 8000:8000 aluga-ai-local:dev
```
Parar/remover:
```powershell
docker stop aluga-ai; docker rm aluga-ai
```

---
## 5. Jenkins: Criar Multibranch Pipeline
1. Jenkins → New Item → Multibranch Pipeline → Nome: `Aluga-Ai`
2. Source → Git → URL: `https://github.com/C14-2025/Aluga_Ai.git`
3. Credentials: (só se repositório privado)
4. Salvar → Scan Repository Now
5. Abrir branch `Actions_to_Jenkins` → Build Now

---
## 6. Parâmetros da Pipeline (Jenkinsfile)
| Parâmetro | Tipo | Default | O que faz |
|-----------|------|---------|-----------|
| RUN_TESTS | boolean | true | Executa todos os estágios de testes e qualidade. |
| BUILD_DOCKER_IMAGE | boolean | false | Constrói imagem Docker da aplicação usando `Dockerfile`. |
| PUSH_TO_REGISTRY | boolean | false | Faz push da imagem para Docker Hub (exige credencial). |
| DEPLOY_APP | boolean | false | Realiza deploy em produção (apenas branch `main`). |
| DOCKERHUB_REPO | string | `seu-usuario/aluga-ai` | Nome do repositório Docker Hub (ex: `usuario/aluga-ai`). |
| CREDENTIALS_ID | string | `dockerhub-credentials` | ID da credencial Jenkins para login Docker. |
| NOTIFY_EMAIL | string | vazio | Email para notificações de sucesso/falha. |

### Ordem lógica
1. Checkout / Prepare sempre executam.
2. Testes e qualidade só rodam se `RUN_TESTS=true`.
3. Build Docker depende de `BUILD_DOCKER_IMAGE=true`.
4. Push depende de `PUSH_TO_REGISTRY=true` E `BUILD_DOCKER_IMAGE=true`.
5. Deploy depende de `DEPLOY_APP=true` E `BUILD_DOCKER_IMAGE=true` e branch `main`.

---
## 7. Cenários Comuns
### A. Desenvolvimento Rápido (somente testes)
```
RUN_TESTS = true
BUILD_DOCKER_IMAGE = false
PUSH_TO_REGISTRY = false
DEPLOY_APP = false
```

### B. Gerar Imagem para validar
```
RUN_TESTS = true
BUILD_DOCKER_IMAGE = true
PUSH_TO_REGISTRY = false
DEPLOY_APP = false
```

### C. Publicar Imagem no Docker Hub
```
RUN_TESTS = true
BUILD_DOCKER_IMAGE = true
PUSH_TO_REGISTRY = true
DEPLOY_APP = false
DOCKERHUB_REPO = seu-usuario/aluga-ai
CREDENTIALS_ID = dockerhub-credentials
```

### D. Deploy (branch main)
```
RUN_TESTS = true
BUILD_DOCKER_IMAGE = true
PUSH_TO_REGISTRY = true
DEPLOY_APP = true
Branch: main
```

---
## 8. Criar Credenciais Docker Hub (quando for fazer push)
1. Jenkins → Manage Jenkins → Credentials → System → Global → Add Credentials
2. Kind: Username with password
3. Username: seu usuário Docker Hub
4. Password: sua senha ou token
5. ID: `dockerhub-credentials`
6. Save

---
## 9. Verificando Resultados
- Relatórios HTML: Stages de testes publicam (BD, API, ETL) se plugin HTML Publisher instalado.
- Artefatos: `report_bd.html`, `report_api.html`, `report_etl.html`, `pylint_report.txt`, `flake8_report.txt`, `server.log`.
- Logs Docker (build/test) somente se imagem habilitada.

---
## 10. Troubleshooting Rápido
| Problema | Causa | Solução |
|----------|-------|---------|
| Falha em venv | Python não instalado na imagem Jenkins | Usar Jenkins oficial e instalar via stage (já faz). |
| Pip não encontra pacote | Dependência faltando | Adicionar ao `requirements.txt` e commit. |
| Push falha (auth) | Credencial errada | Recriar credencial Docker no Jenkins. |
| Deploy bloqueado | Branch != main | Fazer merge para `main`. |
| HTML report não aparece | Plugin ausente | Instalar "HTML Publisher" em Manage Plugins. |

---
## 11. Fluxo Resumido
```
Commit -> Jenkins Build -> Testes -> (Opcional) Build Docker -> (Opcional) Push -> (Opcional) Deploy
```

---
## 12. Glossário
- CI: Integração contínua (testar sempre).
- CD: Entrega contínua (build/push/deploy automatizados).
- Artefato: Arquivo gerado pelo build/test (relatório, log, imagem).
- Imagem Docker: Pacote imutável da aplicação.
- Deploy: Colocar a nova versão rodando.

---
## 13. Checklist Antes de Entregar
- [ ] Jenkins job criado
- [ ] Build "Somente Testes" OK
- [ ] Build "Com Imagem" OK
- [ ] Push (se necessário) OK
- [ ] Deploy (se necessário) OK
- [ ] Documentação lida pelo grupo

---
## 14. Comandos Úteis
```powershell
# Reiniciar Jenkins sem apagar dados
docker-compose restart jenkins

# Limpar totalmente (perde config)
docker-compose down -v

# Ver artefatos do build (no workspace do Jenkins)
# Acesso via interface: Job -> Build -> Workspace
```

---
## 15. Perguntas Frequentes (FAQ)
**Preciso marcar tudo sempre?** Não. Marque só o necessário para o objetivo.
**Posso rodar só build Docker sem testes?** Tecnicamente sim (RUN_TESTS=false, BUILD_DOCKER_IMAGE=true), mas não recomendado.
**Deploy em outra branch?** Bloqueado por design para evitar publicar código sem revisão.

---
## 16. Próximos Passos Melhorias (Ideias)
- Adicionar testes de integração reais.
- Pipeline para gerar imagem multi-stage (menor).
- Webhook para disparar build em cada push sem scan manual.
- Integração de cobertura (coverage.py + report HTML).

---
Feito para a turma: usem, adaptem e perguntem se surgir dúvida.
