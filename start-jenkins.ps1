# Script PowerShell para iniciar o Jenkins CI/CD
# Projeto: Aluga_Ai

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Aluga_Ai - Jenkins CI/CD Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Parando containers anteriores..." -ForegroundColor Yellow
docker-compose down

Write-Host ""
Write-Host "[2/4] Construindo imagem do Jenkins..." -ForegroundColor Yellow
docker-compose build jenkins

Write-Host ""
Write-Host "[3/4] Iniciando Jenkins..." -ForegroundColor Yellow
docker-compose up -d jenkins

Write-Host ""
Write-Host "[4/4] Aguardando Jenkins inicializar..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Jenkins iniciado com sucesso!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Acesse: http://localhost:8080" -ForegroundColor White
Write-Host ""

# Tenta pegar a senha automaticamente
Write-Host "Obtendo senha inicial do Jenkins..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $password = docker exec jenkins-aluga-ai cat /var/jenkins_home/secrets/initialAdminPassword 2>$null
    if ($password) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Senha inicial do Jenkins:" -ForegroundColor White
        Write-Host $password -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        
        # Copia para clipboard
        Set-Clipboard -Value $password
        Write-Host "✓ Senha copiada para a área de transferência!" -ForegroundColor Green
    }
} catch {
    Write-Host "Aguarde mais alguns segundos e execute:" -ForegroundColor Yellow
    Write-Host "docker exec jenkins-aluga-ai cat /var/jenkins_home/secrets/initialAdminPassword" -ForegroundColor White
}

Write-Host ""
Write-Host "Pressione qualquer tecla para ver os logs..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

docker-compose logs -f jenkins
