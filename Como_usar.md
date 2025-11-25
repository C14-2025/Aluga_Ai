# Como rodar o projeto (App + Jenkins CI/CD)

Guia rápido para clonar, rodar a aplicação, subir o Jenkins, habilitar builds automáticos com webhook e publicar imagem no Docker Hub.

## Pré‑requisitos

- Windows com Docker Desktop (com Docker Compose) e Git instalados
- PowerShell (v5+)
- Opcional (para webhook): ngrok (conta gratuita)

## 1. Clonar o repositório

```powershell
git clone https://github.com/C14-2025/Aluga_Ai.git
cd Aluga_Ai
```

## 2. Subir o Jenkins

O Jenkins roda em container com tudo necessário (Python, Docker CLI, plugins).

```powershell
docker-compose up -d --build jenkins
```

Primeiro start (somente na 1ª vez do seu PC):

- Acesse <http://localhost:8080>
- Se pedir senha inicial:

```powershell
docker-compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

- Crie o usuário admin e conclua o assistente (os plugins principais já são instalados pela imagem).

## 3. Criar o job (Multibranch Pipeline)

No Jenkins (<http://localhost:8080>):

1. New Item → Multibranch Pipeline (nome: AlugaAi)
2. Branch Sources → Git

   - Project Repository: <https://github.com/C14-2025/Aluga_Ai.git>

3. Build Configuration: by Jenkinsfile (padrão)
4. Save → clique em “Scan Repository Now”

Isso vai detectar as branches e usar o `Jenkinsfile` do projeto.

## 4. Rodar a aplicação (local, via Docker)

Para subir a app Django para testes locais:

```powershell
docker-compose up -d app
```

Abra <http://localhost:8000>

Para parar:

```powershell
docker-compose down
```

## 5. Executar a pipeline manualmente

No Jenkins → Job “AlugaAi” → Branch desejada (ex.: `Actions_to_Jenkins`) → Build with Parameters.

Parâmetros úteis:

- RUN_TESTS: true/false (executa testes e validações)
- BUILD_DOCKER_IMAGE: true/false (constrói imagem Docker do app)
- PUSH_TO_REGISTRY: true/false (publica no Docker Hub)
- DOCKERHUB_REPO: seu_usuario/aluga-ai
- CREDENTIALS_ID: dockerhub-credentials

## 6. Habilitar builds automáticos (webhook)

Se quiser que cada push no GitHub dispare build imediato:

- Inicie o túnel para o Jenkins

Comandos:

```powershell
ngrok config add-authtoken SEU_TOKEN_NGROK
ngrok http 8080
```

- Copie a URL HTTPS do ngrok (ex.: <https://xxxx.ngrok-free.dev>)
- No GitHub do repositório → Settings → Webhooks → Add webhook
  - Payload URL: <https://xxxx.ngrok-free.dev/github-webhook/>
  - Content type: application/json
  - Just the push event
  - Add webhook

Se não quiser usar ngrok, use “Scan Repository Now” no Jenkins quando precisar.

## 7. Publicar imagem no Docker Hub

- Crie credencial no Jenkins:

  - Manage Jenkins → Credentials → System → Global → Add Credentials
  - Kind: Username with password
    - Username: seu usuário do Docker Hub (ex.: `seuusuario`)
    - Password: sua senha OU um Access Token (se usa login via GitHub/2FA)
    - ID: dockerhub-credentials

- Rode o build com push:

- Build with Parameters:

  - RUN_TESTS: false (opcional para acelerar)
  - BUILD_DOCKER_IMAGE: true
  - PUSH_TO_REGISTRY: true
  - DOCKERHUB_REPO: `seuusuario/aluga-ai`
  - CREDENTIALS_ID: `dockerhub-credentials`

- Verifique no Hub: <https://hub.docker.com/r/seuusuario/aluga-ai> (tags `latest` e a do commit)

## 8. Fluxo de trabalho para alterações de código

- Faça a mudança e commite:

```powershell
git checkout -b minha-feature
git add .
git commit -m "feat: minha mudança"
git push origin minha-feature
```

- Se webhook estiver ativo, o Jenkins builda automaticamente.
- Sem webhook, use “Scan Repository Now” e/ou “Build with Parameters”.

## 9. Onde ver resultados da pipeline

Em um build da branch:

- Console Output: logs completos
- Artifacts: relatórios (ex.: `report_bd.html`, `report_api.html`, `report_etl.html`, `validation_results.json`)
- HTML Reports: links “Report_20BD”, “Report_20API”, “Report_20ETL”

## 10. Problemas comuns

- ngrok caiu (erro ERR_NGROK_3200): reabra `ngrok http 8080` e atualize a URL no webhook
- Docker “permission denied” dentro do Jenkins: use o `docker-compose.yml` do projeto (já configurado). Se necessário, reinicie:

```powershell
docker-compose down
docker-compose up -d --build jenkins
```

- STATIC_ROOT não definido durante build da imagem: já tratamos com `|| true`. Se quiser ajustar definitivamente, adicione `STATIC_ROOT = BASE_DIR / "staticfiles"` no `settings.py`.

---

Pronto! Com isso, qualquer pessoa consegue subir o Jenkins, rodar a app, habilitar webhook e publicar a imagem no Docker Hub.
