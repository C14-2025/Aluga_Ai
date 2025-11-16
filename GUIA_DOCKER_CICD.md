# 🚀 Guia Super Enxuto: CI/CD - Aluga_Ai

## 📋 O que vocês precisam fazer

### 1️⃣ **Criar conta no DockerHub** (Gratuito)
- Acesse: https://hub.docker.com
- Crie uma conta (anota usuário e senha!)
- Exemplo: usuário = `joaosilva`

---

### 2️⃣ **Configurar Jenkins (Primeira vez)**

#### Passo A (opcional agora): Adicionar credenciais Docker
1. Acesse Jenkins: http://localhost:8080
2. Manage Jenkins → Credentials → System → Global credentials
3. Clique "Add Credentials"
4. Preencha:
   ```
   Kind: Username with password
   Username: seu-usuario-dockerhub
   Password: sua-senha-dockerhub
   ID: dockerhub-credentials
   Description: Credenciais DockerHub
   ```
5. Salve

#### Passo B: Criar Multibranch Pipeline (recomendado)
1. Jenkins → New Item → Multibranch Pipeline → Nome: `Aluga-Ai`
2. Source → Git → URL: https://github.com/C14-2025/Aluga_Ai.git
3. (Credencial só se privado)
4. Salvar → Scan Repository Now
5. Entrar em `Actions_to_Jenkins` → Build Now

---

### 3️⃣ **Primeiro Build (descobrir parâmetros)**
Rodar um build simples para o Jenkins registrar os parâmetros do `Jenkinsfile`.

---

### 4️⃣ **Execuções Normais**

#### 🧪 **Só Testar (uso diário):**
```
1. Clique em "Build with Parameters"
2. Configure:
   ☑ RUN_TESTS = true
   ☐ BUILD_DOCKER_IMAGE = false
   ☐ PUSH_TO_REGISTRY = false
   ☐ DEPLOY_APP = false
   NOTIFY_EMAIL = (deixe vazio ou seu email)
3. Clique "Build"
```

**O que acontece:**
- ✅ Roda todos os testes
- ⏭️ Não faz build Docker
- ⏭️ Não publica nada
- ⏱️ ~5 minutos

---

#### 📦 **Criar Imagem (pré-release):**
```
1. Clique em "Build with Parameters"
2. Configure:
   ☑ RUN_TESTS = true
   ☑ BUILD_DOCKER_IMAGE = true
   ☐ PUSH_TO_REGISTRY = false
   ☐ DEPLOY_APP = false
   DOCKERHUB_REPO = seu-usuario/aluga-ai
3. Clique "Build"
```

**O que acontece:**
- ✅ Roda testes
- ✅ Cria imagem Docker localmente
- ⏭️ Não publica ainda
- ⏱️ ~8 minutos

---

#### 🌐 **Publicar no DockerHub:**
```
1. Clique em "Build with Parameters"
2. Configure:
   ☑ RUN_TESTS = true
   ☑ BUILD_DOCKER_IMAGE = true
   ☑ PUSH_TO_REGISTRY = true
   ☐ DEPLOY_APP = false
   DOCKERHUB_REPO = seu-usuario/aluga-ai
   CREDENTIALS_ID = dockerhub-credentials
3. Clique "Build"
```

**O que acontece:**
- ✅ Roda testes
- ✅ Cria imagem Docker
- ✅ **Publica no DockerHub**
- Agora qualquer um pode rodar: `docker run seu-usuario/aluga-ai`
- ⏱️ ~10 minutos

---

#### 🚀 **Deploy (produção / branch main):**
```
1. ATENÇÃO: Só faça na branch MAIN!
2. Clique em "Build with Parameters"
3. Configure:
   ☑ RUN_TESTS = true
   ☑ BUILD_DOCKER_IMAGE = true
   ☑ PUSH_TO_REGISTRY = true
   ☑ DEPLOY_APP = true
   DOCKERHUB_REPO = seu-usuario/aluga-ai
   NOTIFY_EMAIL = seuemail@exemplo.com
4. Clique "Build"
```

**O que acontece:**
- ✅ Pipeline completa
- ✅ Testes → Build → Push → **DEPLOY**
- 🚀 Aplicação sobe em produção
- 📧 Email de confirmação
- ⏱️ ~12 minutos

---

## 🐳 Docker (resumo rápido)

### **Dockerfile** (Já criado ✅)
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

**O que faz:**
- Receita para criar a "caixa" (container)
- Instala Python 3.13
- Instala dependências
- Copia seu código
- Define comando de inicialização

---

### **Build Docker Image** (Stage no Jenkins)
```bash
docker build -t seu-usuario/aluga-ai:123 .
```

**O que faz:**
1. Lê o Dockerfile
2. Cria uma imagem (foto/snapshot) da aplicação
3. Tag: `seu-usuario/aluga-ai:123` (número do build)
4. Imagem fica salva localmente no Jenkins

Analogia: uma caixa portátil com tudo dentro.

---

### **Push to Registry** (Publicar)
```bash
docker push seu-usuario/aluga-ai:123
```

**O que faz:**
1. Envia a imagem para o DockerHub
2. Fica disponível na internet
3. Qualquer servidor pode baixar

Analogia: subir a imagem para um “Drive” público.

---

### **Deploy Application** (Colocar no ar)
```bash
docker pull seu-usuario/aluga-ai:123
docker run -d -p 8000:8000 seu-usuario/aluga-ai:123
```

**O que faz:**
1. Baixa a imagem do DockerHub
2. Inicia o container
3. Aplicação fica acessível na porta 8000

Analogia: instalar e abrir o app.

---

## 🎯 Fluxo Resumido

```
┌─────────────────────────────────────────┐
│ 1. VOCÊ FAZ COMMIT                      │
│    git push origin Actions_to_Jenkins   │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ 2. JENKINS DETECTA MUDANÇA              │
│    "Novo commit! Vou rodar pipeline"    │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ 3. RODA TESTES                          │
│    ✓ Testes BD                          │
│    ✓ Testes API                         │
│    ✓ Testes ETL                         │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ 4. BUILD DOCKER (se marcado)            │
│    Cria "caixa" com a aplicação         │
│    Imagem: aluga-ai:456                 │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ 5. PUSH DOCKERHUB (se marcado)          │
│    Publica no hub.docker.com            │
│    Disponível globalmente               │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ 6. DEPLOY (se marcado + branch main)    │
│    Baixa imagem                         │
│    Para versão antiga                   │
│    Inicia nova versão                   │
│    🚀 APP NO AR!                        │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ 7. NOTIFICAÇÃO EMAIL                    │
│    ✅ Pipeline executada com sucesso    │
│    ou ❌ Algo deu errado                │
└─────────────────────────────────────────┘
```

---

## 🎓 Para Apresentar

### **Mostre:**

1. **GitHub Actions → Jenkins** (migração)
2. **Dockerfile** (containerização)
3. **Jenkinsfile com parâmetros** (flexibilidade)
4. **Execução da pipeline** (testes passando)
5. **Imagem no DockerHub** (publicação)
6. **(Opcional) Deploy rodando** (produção)

### **Explique:**

**"Migramos do GitHub Actions para Jenkins porque:"**

1. ✅ **CI:** Testes automáticos a cada commit
2. ✅ **CD:** Deploy automático se testes passarem
3. ✅ **Docker:** Aplicação containerizada (portável)
4. ✅ **Parâmetros:** Controle fino do que executar
5. ✅ **Notificações:** Email de sucesso/falha

**"O diferencial do nosso projeto:"**
- 🐳 Containerização completa
- 🎛️ Pipeline parametrizada (flexível)
- 📊 Relatórios de qualidade (pylint, flake8)
- 🚀 Deploy automatizado

---

## 🆘 Problemas Comuns

### Problema: "Permission denied" no Docker
**Solução:**
```bash
# No servidor Jenkins
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Problema: "Cannot connect to Docker daemon"
**Solução:**
```bash
# Verificar se Docker está rodando
docker ps

# Se não estiver, iniciar
sudo systemctl start docker
```

### Problema: "Invalid credentials"
**Solução:**
1. Verificar se credenciais estão corretas no Jenkins
2. Testar login manual: `docker login`
3. Recriar credenciais se necessário

---

## 📝 Checklist Antes de Apresentar

- [ ] Jenkins rodando (localhost:8080)
- [ ] DockerHub account criada
- [ ] Credenciais Docker configuradas no Jenkins
- [ ] Job da pipeline criado
- [ ] Pelo menos 1 build com sucesso
- [ ] Imagem publicada no DockerHub (opcional)
- [ ] Entender o que cada stage faz

---

## 💡 Dica Final

Use os parâmetros de forma estratégica:

- **Desenvolvimento diário:** Só RUN_TESTS ✅
- **Antes de apresentar:** Tudo marcado (show completo) ✅✅✅✅

Boa sorte! 🚀
