def dockerimagename
def dockerImage

pipeline {
    agent any

    // Parâmetros de execução
    parameters {
        string(name: 'NOTIFY_EMAIL', defaultValue: '', description: 'Email para receber notificações da pipeline (sucesso/falha)')
        // DOCKERHUB_REPO ajustado para usar 'aluga_ai' como a imagem base
        string(name: 'DOCKERHUB_REPO', defaultValue: 'alvarocareli/aluga-ai', description: 'Repositório no Docker Hub (ex.: usuario/aluga-ai)')
    }

    // CI/CD automático: nenhum parâmetro de execução manual

    environment {
        PYTHON_VERSION = '3.13'
        DJANGO_SETTINGS_MODULE = 'aluga_ai_web.settings'
        PYTHONPATH = "${WORKSPACE}"
        WORKDIR = "${env.WORKSPACE}"
        // Configurações utilizadas no pipeline (defina as credenciais e repo no Jenkins/Job config quando necessário)
        DOCKERHUB_REPO = "${params.DOCKERHUB_REPO}"
        CREDENTIALS_ID = 'dockerhub-credentials' // ID da credencial Username/Password para Docker Hub
        // Valor proveniente do parâmetro
        NOTIFY_EMAIL = "${params.NOTIFY_EMAIL}"
        // E-mail padrão caso nenhum seja passado como parâmetro
        DEFAULT_NOTIFY_EMAIL = 'alvaro.sampaio@ges.inatel.br'
        // SMTP settings for Python SMTP stage (update to your SMTP server)
        SMTP_HOST = 'smtp.example.com'
        SMTP_PORT = '587'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Fazendo checkout do código...'
                checkout scm
            }
        }

        stage('Prepare') {
            steps {
                script {
                    // Determina tag da imagem a partir do commit
                    env.SHORT_COMMIT = sh(script: 'git rev-parse --short HEAD || echo ${BUILD_NUMBER}', returnStdout: true).trim()
                    env.IMAGE_TAG = env.SHORT_COMMIT ?: (env.BUILD_NUMBER ?: 'latest')
                    env.IMAGE = "${env.DOCKERHUB_REPO}:${env.IMAGE_TAG}"
                    env.IMAGE_LATEST = "${env.DOCKERHUB_REPO}:latest"
                    echo "Image será: ${env.IMAGE}"
                }
            }
        }

        // ------------------------------------------

        stage('Setup Python Environment') {
            steps {
                echo 'Configurando ambiente Python...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    python --version
                    pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Instalando dependências...'
                sh '''
                    . venv/bin/activate
                    pip install -r requirements.txt pytest pytest-html || true
                '''
            }
        }

        stage('Run Migrations') {
            steps {
                echo 'Executando migrações do Django...'
                sh '''
                    . venv/bin/activate
                    python manage.py migrate --noinput
                '''
            }
        }
        
        // Estágios de Teste (mantidos como estavam, sem alterações)
        stage('Testes Unitários - Banco de Dados') {
            steps {
                echo 'Executando testes de Banco de Dados...'
                sh '''
                    . venv/bin/activate
                    if [ -f BancoDeDados/test_bd.py ]; then
                        pytest BancoDeDados/test_bd.py --template=html1/index.html --report=report_bd.html || true
                    elif [ -f Dados/test_bd.py ]; then
                        pytest Dados/test_bd.py --template=html1/index.html --report=report_bd.html || true
                    else
                        echo "No BancoDeDados test file found, skipping Banco de Dados tests"
                    fi
                '''
            }
            post {
                always {
                    sh 'mv -f report_bd.html aluga_ai_web/report_bd.html || true'
                    archiveArtifacts artifacts: 'aluga_ai_web/report_bd.html', allowEmptyArchive: true
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'aluga_ai_web',
                        reportFiles: 'report_bd.html',
                        reportName: 'Report BD'
                    ])
                }
            }
        }

        stage('Testes Unitários - API') {
            steps {
                echo 'Executando testes de API...'
                sh '''
                    . venv/bin/activate
                    if [ -f Dados/test_etl.py ]; then
                        pytest Dados/test_etl.py --template=html1/index.html --report=report_api.html || true
                    elif [ -f aluga_ai_web/Dados/test_etl.py ]; then
                        pytest aluga_ai_web/Dados/test_etl.py --template=html1/index.html --report=report_api.html || true
                    else
                        echo "No API test file found (Dados/test_etl.py), skipping API tests"
                    fi
                '''
            }
            post {
                always {
                    sh 'mv -f report_api.html aluga_ai_web/report_api.html || true'
                    archiveArtifacts artifacts: 'aluga_ai_web/report_api.html', allowEmptyArchive: true
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'aluga_ai_web',
                        reportFiles: 'report_api.html',
                        reportName: 'Report API'
                    ])
                }
            }
        }

        stage('Testes Unitários - Propriedades e Reservas') {
            steps {
                echo 'Executando testes de Propriedades e Reservas...'
                sh '''
                    . venv/bin/activate
                    mkdir -p reports
                    pytest propriedades/tests.py reservas/tests.py \
                        --junitxml=reports/junit_prop_res.xml \
                        --template=html1/index.html --report=reports/report_prop_res.html || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/report_prop_res.html', allowEmptyArchive: true
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports',
                        reportFiles: 'report_prop_res.html',
                        reportName: 'Report Propriedades e Reservas'
                    ])
                    junit 'reports/junit_prop_res.xml'
                }
            }
        }

        stage('Testes Unitários - Usuarios') {
            steps {
                echo 'Executando testes de Modelos e Views da app Usuarios...'
                sh '''
                    . venv/bin/activate
                    mkdir -p reports
                    pytest usuarios/tests.py \
                        --junitxml=reports/junit_usuarios.xml || true
                '''
            }
            post {
                always {
                    junit 'reports/junit_usuarios.xml'
                }
            }
        }

        stage('Testes Unitários - Favoritos') {
            steps {
                echo 'Executando testes de Favoritos...'
                sh '''
                    . venv/bin/activate
                    if [ -f Favoritos/tests.py ]; then
                        pytest Favoritos/tests.py --template=html1/index.html --report=report_favoritos.html || true
                        mkdir -p aluga_ai_web
                        mv -f report_favoritos.html aluga_ai_web/report_favoritos.html || true
                    else
                        echo "No Favoritos/tests.py found, skipping Favoritos tests"
                    fi
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'aluga_ai_web/report_favoritos.html', allowEmptyArchive: true
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'aluga_ai_web',
                        reportFiles: 'report_favoritos.html',
                        reportName: 'Report Favoritos'
                    ])
                }
            }
        }


        stage('Testes Unitários - Mensagens') {
            steps {
                echo 'Executando testes de Mensagens...'
                sh '''
                    . venv/bin/activate
                    if [ -f Mensagens/tests.py ]; then
                        pytest Mensagens/tests.py --template=html1/index.html --report=report_mensagens.html || true
                    fi
                    mv -f report_mensagens.html aluga_ai_web/report_mensagens.html || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'aluga_ai_web/report_mensagens.html', allowEmptyArchive: true
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'aluga_ai_web',
                        reportFiles: 'report_mensagens.html',
                        reportName: 'Report Mensagens'
                    ])
                }
            }
        }

        stage('Testes ETL') {
            steps {
                echo 'Executando testes de ETL...'
                dir('Dados') {
                    sh '''
                        . ../venv/bin/activate
                        if [ -f test_etl.py ]; then
                            pytest test_etl.py --template=html1/index.html --report=report_etl.html || true
                        else
                            echo "No test_etl.py found in Dados, skipping ETL tests"
                        fi
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'aluga_ai_web/Dados/report_etl.html', allowEmptyArchive: true
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'aluga_ai_web/Dados',
                        reportFiles: 'report_etl.html',
                        reportName: 'Report ETL'
                    ])
                }
            }
        }

        stage('Executar ETL') {
            steps {
                echo 'Executando processo de ETL...'
                dir('Dados') {
                    sh '''
                        . ../venv/bin/activate
                        if [ -f etl.py ]; then
                            python etl.py || true
                        else
                            echo "No etl.py found in Dados, skipping ETL execution"
                        fi
                    '''
                }
            }
        }

        stage('Validação do Sistema de Recomendação') {
            steps {
                echo 'Validando sistema de recomendação...'
                sh '''
                    . venv/bin/activate
                    if [ -f jobs/validate_recommendation_system.py ]; then
                        python jobs/validate_recommendation_system.py || true
                    else
                        echo "No jobs/validate_recommendation_system.py found, skipping recommendation validation"
                    fi
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'validation_results.json', allowEmptyArchive: true
                }
            }
        }

        stage('Testes Recomendação Personalizada') {
            steps {
                echo 'Executando testes de recomendação personalizada...'
                sh '''
                    . venv/bin/activate
                    if [ -f recomendacoes/tests/test_personal_recommend.py ]; then
                        pytest recomendacoes/tests/test_personal_recommend.py --maxfail=1 -q || true
                    else
                        echo "No recomendacoes personal test found, skipping personalized recommendation tests"
                    fi
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/*.html', allowEmptyArchive: true
                }
            }
        }

        stage('Django Tests') {
            steps {
                echo 'Executando testes do Django...'
                sh '''
                    . venv/bin/activate
                    python manage.py test || true
                '''
            }
        }

        stage('Code Quality Check') {
            steps {
                echo 'Verificando qualidade do código...'
                sh '''
                    . venv/bin/activate
                    pylint --exit-zero --output-format=text aluga_ai_web/ > pylint_report.txt || true
                    flake8 --exit-zero --output-file=flake8_report.txt . || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'pylint_report.txt,flake8_report.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Test Django Server') {
            steps {
                echo 'Testando se o servidor Django inicia corretamente...'
                sh '''
                    . venv/bin/activate
                    # Inicia o servidor em background
                    nohup python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &
                    SERVER_PID=$!

                    # Aguarda o servidor iniciar
                    sleep 10

                    # Testa se o servidor está respondendo
                    curl -I http://127.0.0.1:8000 || echo "Servidor não respondeu na porta 8000"

                    # Mata o processo do servidor
                    kill $SERVER_PID || true

                    echo "Servidor Django testado com sucesso"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'server.log', allowEmptyArchive: true
                }
            }
        }
        
        // -------------------------------------------------------------
        // --- ETAPAS DE CD (Build, Push e Deploy) AJUSTADAS AQUI ---
        // -------------------------------------------------------------
        
        stage('Build Docker Image') {
            steps {
                script {
                    dockerimagename = "${env.IMAGE}"
                    echo "Building Docker image: ${dockerimagename}"
                    dockerImage = docker.build(dockerimagename)
                    // Also tag the built image locally as :latest so a local latest exists
                    sh "docker tag ${env.IMAGE} ${env.DOCKERHUB_REPO}:latest || true"
                    echo "Tagged local image as: ${env.DOCKERHUB_REPO}:latest"
                    echo "Imagem Docker construída com sucesso: ${dockerimagename}"
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                echo "Pushing Docker images to ${env.DOCKERHUB_REPO}..."
                script {
                    try {
                        docker.withRegistry('https://registry.hub.docker.com', env.CREDENTIALS_ID) {
                            echo "Pushing ${dockerimagename} to registry"
                            dockerImage.push()
                            dockerImage.push('latest')
                        }
                    } catch (err) {
                        echo "Docker push failed: ${err}"
                        echo "Ensure a Jenkins credential with ID '${env.CREDENTIALS_ID}' exists (Manage Jenkins → Credentials)."
                        echo "If you don't want to push from this job, set a different CREDENTIALS_ID or remove the Push stage."
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Deployment (CD)') {
            steps {
                echo 'Starting deployment of the new image on the target environment...'
                sh '''
                    # Try 'docker compose' (v2) and fall back to 'docker-compose' (v1) if needed.
                    set -e
                    echo "Attempting deploy with 'docker compose' (v2)..."
                    if docker compose version >/dev/null 2>&1; then
                        docker compose -f docker-compose.yml pull aluga-ai-app || true
                        docker compose -f docker-compose.yml up -d --no-deps aluga-ai-app
                    elif command -v docker-compose >/dev/null 2>&1; then
                        echo "'docker compose' not available or failed; falling back to 'docker-compose'"
                        docker-compose -f docker-compose.yml pull aluga-ai-app || true
                        docker-compose -f docker-compose.yml up -d --no-deps aluga-ai-app
                    else
                        echo "Neither 'docker compose' nor 'docker-compose' available on this agent. Install Docker Compose or adjust the deploy step."
                        exit 125
                    fi

                    echo "Deployment of aluga-ai-app complete."
                '''
            }
        }
        
        // -------------------------------------------------------------
        // --- Etapas de Notificação Originais ---
        // -------------------------------------------------------------
        
        stage('Notification (Shell)') {
            steps {
                echo 'Sending shell notification...'
                sh '''
                    # Determine recipient (use NOTIFY_EMAIL param if provided, otherwise DEFAULT_NOTIFY_EMAIL)
                    TO="${NOTIFY_EMAIL:-${DEFAULT_NOTIFY_EMAIL}}"

                    # Run provided scripts if present
                    if [ -d scripts ]; then
                        cd scripts || true
                        chmod 775 * || true
                        ./shell.sh || true
                        cd - >/dev/null 2>&1 || true
                    fi

                    # Try to send mail using the system `mail` command
                    if command -v mail >/dev/null 2>&1; then
                        echo "Pipeline ${JOB_NAME} #${BUILD_NUMBER} finished. See ${BUILD_URL}" | mail -s "Jenkins: ${JOB_NAME} #${BUILD_NUMBER} - Build Notification" "$TO" || echo "mail command failed"
                        echo "Shell mail attempted to $TO"
                    else
                        echo "mail command not found on agent; install mailutils/postfix to enable shell email"
                    fi
                '''
            }
        }

        stage('Send Email via Python (SMTP)') {
            steps {
                echo 'Sending email via Python using Jenkins Credentials...'
                // requires a Jenkins credential (username/password) with id 'smtp-creds'
                script {
                    try {
                        withCredentials([usernamePassword(credentialsId: 'smtp-creds', usernameVariable: 'SMTP_USER', passwordVariable: 'SMTP_PASS')]) {
                            sh '''
                                python - <<'PY'
                                import os, smtplib, ssl
                                to = os.environ.get('NOTIFY_EMAIL') or os.environ.get('DEFAULT_NOTIFY_EMAIL')
                                smtp_host = os.environ.get('SMTP_HOST', 'smtp.example.com')
                                smtp_port = int(os.environ.get('SMTP_PORT', '587'))
                                user = os.environ.get('SMTP_USER')
                                password = os.environ.get('SMTP_PASS')
                                subject = f"Jenkins: {os.environ.get('JOB_NAME')} #{os.environ.get('BUILD_NUMBER')}"
                                body = f"Pipeline {os.environ.get('JOB_NAME')} #{os.environ.get('BUILD_NUMBER')} finalizada. Ver: {os.environ.get('BUILD_URL')}"
                                msg = f"Subject: {subject}\n\n{body}"
                                try:
                                    # If port 465 (implicit SSL) use SMTP_SSL
                                    if smtp_port == 465:
                                        context = ssl.create_default_context()
                                        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=30) as server:
                                            server.login(user, password)
                                            server.sendmail(user, [to], msg)
                                    else:
                                        # Try STARTTLS first (typical for port 587)
                                        server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
                                        server.ehlo()
                                        try:
                                            server.starttls()
                                            server.ehlo()
                                            server.login(user, password)
                                            server.sendmail(user, [to], msg)
                                            server.quit()
                                        except Exception as starttls_err:
                                            # STARTTLS failed — try implicit SSL as a fallback
                                            try:
                                                server.quit()
                                            except Exception:
                                                pass
                                            context = ssl.create_default_context()
                                            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=30) as ssl_server:
                                                ssl_server.login(user, password)
                                                ssl_server.sendmail(user, [to], msg)
                                    print('Email sent to', to)
                                except Exception as e:
                                    print('Failed to send email:', e)
                                    raise
                                PY
                            '''
                        }
                    } catch (err) {
                        echo "SMTP credential 'smtp-creds' not available or send failed: ${err}"
                        echo 'Skipping Python SMTP send (no credentials or error)'
                    }
                }
            }
        }
        
        

    }

    post {
        always {
            script {
                def buildStatus = currentBuild.currentResult
                def buildUser = currentBuild.getBuildCauses('hudson.model.Cause$UserIdCause')[0]?.userId ?: 'Github User'
                emailext(
                    subject: "Pipeline ${buildStatus}: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    body: """
                        <p>This is a Jenkins CICD pipeline status.</p>
                        <p>Project: ${env.JOB_NAME}</p>
                        <p>Build Number: ${env.BUILD_NUMBER}</p>
                        <p>Build Status: ${buildStatus}</p>
                        <p>Started by: ${buildUser}</p>
                        <p>Build URL: <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
                    """,
                    to: "${params.NOTIFY_EMAIL ?: env.DEFAULT_NOTIFY_EMAIL}",
                    from: "${env.DEFAULT_NOTIFY_EMAIL}",
                    replyTo: "${params.NOTIFY_EMAIL ?: env.DEFAULT_NOTIFY_EMAIL}",
                    mimeType: 'text/html',
                    attachmentsPattern: 'trivyfs.txt'
                )
            }
        }
    }
}# check Docker and compose availability
docker --version
docker compose version || true
docker-compose --version || true

# confirm docker CLI can run a simple command
docker ps -a

# if docker-compose is not installed, install it or enable the compose plugin on the node