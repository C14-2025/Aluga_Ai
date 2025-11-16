@echo off
REM Script para iniciar o ambiente Jenkins CI/CD
REM Projeto: Aluga_Ai

echo ========================================
echo  Aluga_Ai - Jenkins CI/CD Setup
echo ========================================
echo.

echo [1/4] Parando containers anteriores...
docker-compose down

echo.
echo [2/4] Construindo imagem do Jenkins...
docker-compose build jenkins

echo.
echo [3/4] Iniciando Jenkins...
docker-compose up -d jenkins

echo.
echo [4/4] Aguardando Jenkins inicializar...
timeout /t 30 /nobreak

echo.
echo ========================================
echo  Jenkins iniciado com sucesso!
echo ========================================
echo.
echo Acesse: http://localhost:8080
echo.
echo Para obter a senha inicial, execute:
echo docker exec jenkins-aluga-ai cat /var/jenkins_home/secrets/initialAdminPassword
echo.

REM Tenta pegar a senha automaticamente
echo Senha inicial do Jenkins:
docker exec jenkins-aluga-ai cat /var/jenkins_home/secrets/initialAdminPassword 2>nul

echo.
echo Pressione qualquer tecla para ver os logs...
pause >nul

docker-compose logs -f jenkins
