# Guia de Uso - Jenkins com Docker para Aluga_Ai

## 📋 Arquivos Criados

1. **Dockerfile.jenkins** - Imagem customizada do Jenkins com Python
2. **Dockerfile** - Imagem da aplicação Django
3. **docker-compose.yml** - Orquestração dos containers
4. **Jenkinsfile** - Pipeline CI/CD
5. **.dockerignore** - Otimização do build Docker

## 🚀 Como Usar

### 1. Subir o Jenkins

```powershell
# Build e iniciar o Jenkins
docker-compose up -d jenkins

# Ver logs do Jenkins
docker-compose logs -f jenkins
```

### 2. Configurar o Jenkins (Primeira vez)

1. Acesse: http://localhost:8080
2. Pegue a senha inicial:
   ```powershell
   docker exec jenkins-aluga-ai cat /var/jenkins_home/secrets/initialAdminPassword
   ```
3. Instale os plugins sugeridos
4. Instale plugins adicionais necessários:
   - **Pipeline**
   - **Git Plugin**
   - **Docker Plugin**
   - **HTML Publisher**
   - **Email Extension Plugin**

### 3. Criar Job no Jenkins

1. No Jenkins, clique em "New Item"
2. Digite o nome: "Aluga-Ai-Pipeline"
3. Selecione "Pipeline" e clique OK
4. Em "Pipeline":
   - Definition: "Pipeline script from SCM"
   - SCM: Git
   - Repository URL: [URL do seu repositório]
   - Branch: */main (ou sua branch)
   - Script Path: Jenkinsfile
5. Salve

### 4. Configurar Email (Opcional)

No Jenkins, vá em:
- Manage Jenkins → Configure System → Extended E-mail Notification
- Configure seu servidor SMTP
- Adicione a variável de ambiente `NOTIFY_EMAIL` no job

### 5. Testar a Aplicação Localmente

```powershell
# Subir toda a stack
docker-compose up -d

# Verificar status
docker-compose ps

# Acessar a aplicação
# http://localhost:8000

# Acessar o Jenkins
# http://localhost:8080

# Ver logs
docker-compose logs -f app
```

### 6. Build Manual da Aplicação

```powershell
# Build da imagem
docker build -t aluga-ai:latest .

# Rodar container
docker run -p 8000:8000 aluga-ai:latest
```

## 🔧 Comandos Úteis

```powershell
# Parar todos os containers
docker-compose down

# Parar e remover volumes
docker-compose down -v

# Rebuild dos containers
docker-compose build --no-cache

# Ver logs específicos
docker-compose logs -f jenkins
docker-compose logs -f app

# Entrar no container
docker exec -it jenkins-aluga-ai bash
docker exec -it aluga-ai-app bash

# Limpar volumes órfãos
docker volume prune

# Limpar imagens antigas
docker image prune -a
```

## 📊 Diferenças do Maven para Python

### No exemplo do professor (Maven):
```dockerfile
# Instalava Maven
RUN wget apache-maven-3.9.5-bin.tar.gz
ENV MAVEN_HOME /opt/maven
```

### Na nossa solução (Python):
```dockerfile
# Instala Python e pip
RUN apt-get install -y python3 python3-pip python3-venv
RUN pip install pytest pytest-django
```

## 🎯 Fluxo da Pipeline

1. **Checkout** - Baixa o código
2. **Setup** - Configura ambiente Python
3. **Install Dependencies** - Instala requirements.txt
4. **Migrations** - Executa migrações Django
5. **Testes BD** - Testa banco de dados
6. **Testes API** - Testa APIs
7. **Testes ETL** - Testa ETL
8. **ETL** - Executa ETL
9. **Validação** - Valida sistema de recomendação
10. **Django Tests** - Testes do Django
11. **Build** - Cria imagem Docker
12. **Deploy** - Sobe a aplicação (branch main)
13. **Notificação** - Envia email

## ⚠️ Problemas Comuns

### Jenkins não inicia
```powershell
# Verificar logs
docker-compose logs jenkins

# Verificar permissões
docker exec -it jenkins-aluga-ai ls -la /var/jenkins_home
```

### Erro de permissão Docker
```powershell
# No Dockerfile.jenkins já configuramos:
RUN usermod -aG docker jenkins
```

### Pipeline falha nos testes
- Verifique se todas as dependências estão no requirements.txt
- Confirme que o SQLite está funcionando
- Veja os relatórios HTML gerados

## 🔐 Segurança

Para produção, configure:
1. Credenciais do Git no Jenkins
2. Secrets para email
3. Variáveis de ambiente sensíveis
4. HTTPS no Jenkins
5. Backup do volume jenkins_home

## 📝 Próximos Passos

1. Configure webhooks no GitHub para trigger automático
2. Adicione análise de código (pylint, flake8)
3. Configure ambientes de staging/produção
4. Implemente testes de integração
5. Configure monitoramento e alertas
