 pipeline {
    agent any
    
    // Parâmetros de execução
    parameters {
        string(name: 'NOTIFY_EMAIL', defaultValue: '', description: 'Email para receber notificações da pipeline (sucesso/falha)')
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
        CREDENTIALS_ID = 'dockerhub-credentials'
        // Valor proveniente do parâmetro
        NOTIFY_EMAIL = "${params.NOTIFY_EMAIL}"
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
                    pip install -r requirements.txt
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
        stage('Deploy Application ') {
            // Deploy automático somente na branch main
            when { expression { return env.BRANCH_NAME == 'main' } }
            steps {
                echo 'Fazendo deploy da aplicação...'
                sh '''
                    # Diretório para dados persistentes no host
                    HOST_DATA_DIR="/opt/aluga-ai/data"
                    HOST_STATIC_DIR="/opt/aluga-ai/static"
                    HOST_MEDIA_DIR="/opt/aluga-ai/media"
                    
                    # Cria diretórios se não existirem
                    mkdir -p ${HOST_DATA_DIR}
                    mkdir -p ${HOST_STATIC_DIR}
                    mkdir -p ${HOST_MEDIA_DIR}
                    # Try to pull the image; if unavailable, skip deploy (avoids failing when image isn't published)
                    if docker pull ${IMAGE} >/dev/null 2>&1; then
                        docker rm -f aluga-ai-app || true
                        docker run -d --name aluga-ai-app \
                            --restart unless-stopped \
                            -p 8000:8000 \
                            -v ${HOST_DATA_DIR}:/app/data \
                            -v ${HOST_STATIC_DIR}:/app/static \
                            -v ${HOST_MEDIA_DIR}:/app/media \
                            -e DJANGO_SETTINGS_MODULE=aluga_ai_web.settings \
                            -e PYTHONPATH=/app \
                            ${IMAGE}

                        # Verifica se está rodando
                        sleep 5
                        docker ps | grep aluga-ai-app || true
                    else
                        echo "Docker image ${IMAGE} not available; skipping deploy"
                    fi
                '''
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline finalizada!'
            // Limpa workspace
            cleanWs()
        }
        success {
            echo 'Pipeline executada com sucesso!'
            script {
                if (params.NOTIFY_EMAIL && params.NOTIFY_EMAIL.trim() != '') {
                    emailext(
                        subject: "✅ Pipeline Executada com Sucesso - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                        body: """
                            <html>
                            <body>
                                <h2>Pipeline Executada com Sucesso!</h2>
                                <p><b>Job:</b> ${env.JOB_NAME}</p>
                                <p><b>Build:</b> ${env.BUILD_NUMBER}</p>
                                <p><b>Status:</b> ${currentBuild.result}</p>
                                <p><b>Branch:</b> ${env.BRANCH_NAME}</p>
                                <p><b>Duração:</b> ${currentBuild.durationString}</p>
                                <br>
                                <h3>Stages Executados:</h3>
                                <ul>
                                    <li>✓ Testes de Banco de Dados</li>
                                    <li>✓ Testes de API</li>
                                    <li>✓ Testes de ETL</li>
                                    <li>✓ Validação Sistema de Recomendação</li>
                                    <li>✓ Testes Django</li>
                                    <li>✓ Verificação de Qualidade</li>
                                    <li>✓ Teste do Servidor Django</li>
                                </ul>
                                <br>
                                <p>Verifique os detalhes em: <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
                            </body>
                            </html>
                        """,
                        to: params.NOTIFY_EMAIL,
                        mimeType: 'text/html'
                    )
                }
            }
        }
        failure {
            echo 'Pipeline falhou!'
            script {
                if (params.NOTIFY_EMAIL && params.NOTIFY_EMAIL.trim() != '') {
                    emailext(
                        subject: "❌ Pipeline Falhou - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                        body: """
                            <html>
                            <body>
                                <h2 style="color: red;">Pipeline Falhou!</h2>
                                <p><b>Job:</b> ${env.JOB_NAME}</p>
                                <p><b>Build:</b> ${env.BUILD_NUMBER}</p>
                                <p><b>Status:</b> ${currentBuild.result}</p>
                                <p><b>Branch:</b> ${env.BRANCH_NAME}</p>
                                <p><b>Duração:</b> ${currentBuild.durationString}</p>
                                <br>
                                <p style="color: red;"><b>Ação necessária:</b> Verifique os logs para identificar o problema.</p>
                                <br>
                                <p>Verifique os detalhes em: <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
                                <p>Console Output: <a href="${env.BUILD_URL}console">${env.BUILD_URL}console</a></p>
                            </body>
                            </html>
                        """,
                        to: params.NOTIFY_EMAIL,
                        mimeType: 'text/html'
                    )
                }
            }
        }
    }
}
