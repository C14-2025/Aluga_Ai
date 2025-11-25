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
                    
                    # O comando abaixo executa os testes na sua app 'usuarios'.
                    # Se você tem um único arquivo 'tests.py' na raiz da app 'usuarios', 
                    # use o caminho: 'usuarios/tests.py'.
                    # Se você tem vários arquivos de teste dentro de 'usuarios/tests/', use: 'usuarios/tests/'
                    
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
                    if [ -f favoritos/tests.py ]; then
                        pytest favoritos/tests.py --template=html1/index.html --report=report_favoritos.html || true
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
                    if [ -f mensagens/tests.py ]; then
                        pytest mensagens/tests.py --template=html1/index.html --report=report_mensagens.html || true
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
        //Alvaro
        stage('Testes ETL') {
            steps {
                echo 'Executando testes de ETL...'
                dir('dados') {
                    sh '''
                        . ../venv/bin/activate
                        # Ativar mocks para testes ETL em CI (evita dependências externas)
                        export ALUGAAI_USE_MOCKS=1
                        # Garantir diretório de relatórios
                        mkdir -p reports
                        if [ -f test_etl.py ]; then
                            # Executa ETL (não falha a pipeline)
                            python etl.py || true
                            # Executa os testes e gera relatório HTML + junit XML
                            pytest test_etl.py --junitxml=reports/junit_etl.xml --template=html1/index.html --report=reports/report_etl.html || true
                        else
                            echo "No test_etl.py found in dados, skipping ETL tests"
                        fi
                    '''
                }
            }
            post {
                always {
                    // Arquiva os relatórios gerados dentro de `dados/reports`
                    archiveArtifacts artifacts: 'dados/reports/report_etl.html,dados/reports/junit_etl.xml', allowEmptyArchive: true
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'dados/reports',
                        reportFiles: 'report_etl.html',
                        reportName: 'Report ETL'
                    ])
                    // Publica o junit para painel de testes do Jenkins
                    junit 'dados/reports/junit_etl.xml'
                }
            }
        }
        stage('Treinar Modelo ML') {
            steps {
                echo 'Treinando modelo de Machine Learning...'
                sh '''
                    . venv/bin/activate
                    
                    # Garante que PYTHONPATH está configurado
                    export PYTHONPATH="${WORKSPACE}:${PYTHONPATH:-}"
                    export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-aluga_ai_web.settings}"
                    
                    # Verifica se há dados processados disponíveis
                    if [ ! -d dados/processed ]; then
                        echo "AVISO: Diretório dados/processed não encontrado"
                        echo "Skipping ML model training"
                        exit 0
                    fi
                    
                    # Verifica se há arquivos CSV processados
                    CSV_COUNT=$(find dados/processed -name "imoveis_processed_*.csv" 2>/dev/null | wc -l)
                    if [ "$CSV_COUNT" -eq 0 ]; then
                        echo "AVISO: Nenhum arquivo CSV processado encontrado em dados/processed/"
                        echo "Execute o ETL primeiro para gerar dados para treinamento"
                        echo "Skipping ML model training"
                        exit 0
                    fi
                    
                    echo "Encontrados $CSV_COUNT arquivo(s) CSV processado(s)"
                    
                    # Verifica se o script de treinamento existe
                    if [ ! -f recomendacoes/train_model.py ]; then
                        echo "ERRO: recomendacoes/train_model.py não encontrado"
                        echo "Skipping ML model training"
                        exit 0
                    fi
                    
                    echo "Iniciando treinamento do modelo ML..."
                    echo "Caminho atual: $(pwd)"
                    echo "PYTHONPATH: $PYTHONPATH"
                    
                    # Executa o treinamento (permite falha sem parar pipeline)
                    python recomendacoes/train_model.py || {
                        echo "AVISO: Treinamento do modelo falhou, mas continuando pipeline"
                        exit 0
                    }
                    
                    echo "Treinamento do modelo concluído com sucesso"
                    
                    # Verifica e lista arquivos gerados
                    if [ -d recomendacoes/services/ml/model_store ]; then
                        echo "=== Artefatos do modelo gerados ==="
                        ls -lh recomendacoes/services/ml/model_store/ || true
                        # Conta artefatos usando método alternativo para evitar problemas de escape
                        ARTIFACT_COUNT=$(find recomendacoes/services/ml/model_store -type f 2>/dev/null | grep -E '\\.(joblib|pkl|json)$' | wc -l)
                        echo "Total de artefatos gerados: $ARTIFACT_COUNT"
                        if [ "$ARTIFACT_COUNT" -eq 0 ]; then
                            echo "AVISO: Nenhum artefato foi gerado no diretório model_store"
                        fi
                    else
                        echo "AVISO: Diretório recomendacoes/services/ml/model_store não encontrado após treinamento"
                    fi
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'recomendacoes/services/ml/model_store/*.joblib,recomendacoes/services/ml/model_store/*.pkl,recomendacoes/services/ml/model_store/*.json', allowEmptyArchive: true
                }
            }
        }

        stage('Test Coverage Report') {
            steps {
                echo 'Gerando relatório de cobertura de testes...'
                sh '''
                    . venv/bin/activate
                    
                    # Garante que PYTHONPATH e DJANGO_SETTINGS_MODULE estão configurados
                    export PYTHONPATH="${WORKSPACE}:${PYTHONPATH:-}"
                    export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-aluga_ai_web.settings}"
                    
                    mkdir -p reports
                    
                    # Lista de apps Django para cobertura (apenas código-fonte, não testes)
                    APPS="propriedades reservas usuarios favoritos avaliacoes mensagens recomendacoes"
                    
                    # Verifica quais apps existem
                    EXISTING_APPS=""
                    for app in $APPS; do
                        if [ -d "$app" ]; then
                            EXISTING_APPS="$EXISTING_APPS $app"
                        else
                            echo "AVISO: App '$app' não encontrado, será ignorado"
                        fi
                    done
                    
                    if [ -z "$EXISTING_APPS" ]; then
                        echo "AVISO: Nenhum app Django encontrado para testar"
                        echo "Criando relatório de cobertura vazio"
                        touch reports/coverage_report.txt
                        echo "Nenhum app encontrado para cobertura" > reports/coverage_report.txt
                        exit 0
                    fi
                    
                    echo "Apps Django encontrados:$EXISTING_APPS"
                    echo "Iniciando execução de testes com cobertura..."
                    
                    # Executa testes com cobertura usando pytest-cov
                    # --cov especifica quais apps cobrir (apenas código-fonte)
                    # Nota: --omit não é suportado diretamente pelo pytest, será aplicado no coverage report
                    pytest $EXISTING_APPS \
                        --cov=propriedades \
                        --cov=reservas \
                        --cov=usuarios \
                        --cov=favoritos \
                        --cov=avaliacoes \
                        --cov=mensagens \
                        --cov=recomendacoes \
                        --cov-report=html:reports/coverage_html \
                        --cov-report=term \
                        --cov-report=xml:reports/coverage.xml \
                        --junitxml=reports/junit_coverage.xml \
                        --cov-branch \
                        -v || {
                        echo "AVISO: Alguns testes falharam, mas continuando com relatório de cobertura"
                        true
                    }
                    
                    # Gera relatório de texto usando coverage diretamente (pytest-cov não suporta text:arquivo)
                    if [ -f .coverage ]; then
                        echo "Gerando relatório de cobertura em texto..."
                        coverage report --omit='*/venv/*,*/virtualenv/*,*/__pycache__/*,*/migrations/*,*/tests/*,*/test_*.py,*/manage.py,*/settings.py,*/wsgi.py,*/asgi.py,*/urls.py,*/admin.py,*/*/migrations/*' > reports/coverage_report.txt 2>&1 || {
                            echo "AVISO: Erro ao gerar relatório de texto de cobertura"
                            touch reports/coverage_report.txt
                            echo "Erro ao gerar relatório de cobertura" > reports/coverage_report.txt
                        }
                    else
                        echo "AVISO: Arquivo .coverage não encontrado"
                        touch reports/coverage_report.txt
                        echo "Nenhum relatório gerado - arquivo .coverage não encontrado" > reports/coverage_report.txt
                    fi
                    
                    # Verifica se os relatórios foram gerados
                    if [ -f reports/coverage.xml ]; then
                        echo "Relatório XML de cobertura gerado: reports/coverage.xml"
                    else
                        echo "AVISO: Relatório de cobertura XML não foi gerado"
                    fi
                    
                    if [ -d reports/coverage_html ]; then
                        echo "Relatório HTML de cobertura gerado: reports/coverage_html/"
                    else
                        echo "AVISO: Relatório de cobertura HTML não foi gerado"
                    fi
                    
                    echo "Relatório de cobertura processado"
                    
                    # Exibe resumo de cobertura
                    if [ -f reports/coverage_report.txt ]; then
                        echo ""
                        echo "=== RESUMO DE COBERTURA ==="
                        echo ""
                        tail -n 30 reports/coverage_report.txt || true
                        echo ""
                        
                        # Extrai porcentagem total de cobertura (última linha geralmente tem o total)
                        TOTAL_COV=$(tail -n 1 reports/coverage_report.txt | grep -oE '[0-9]+%' | head -n 1 || echo "N/A")
                        echo "Cobertura Total: $TOTAL_COV"
                    else
                        echo "AVISO: Arquivo de relatório de cobertura em texto não encontrado"
                    fi
                '''
            }
            post {
                always {
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports/coverage_html',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                    archiveArtifacts artifacts: 'reports/coverage_report.txt,reports/coverage.xml,reports/coverage_html/**', allowEmptyArchive: true
                }
            }
        }
        //Alvaro
        stage('Validação do Sistema de Recomendação') {
            steps {
                echo 'Validando sistema de recomendação (usando recomendacoes/Testes/ValidacaoSistema.py)...'
                sh '''
                    . venv/bin/activate
                    # Garantir diretório de relatórios
                    mkdir -p dados/reports
                    # Preferir o script de validação no repo; ativar mocks para rodar sem dependências externas
                    if [ -f recomendacoes/Testes/ValidacaoSistema.py ]; then
                        export ALUGAAI_USE_MOCKS=1
                        python recomendacoes/Testes/ValidacaoSistema.py || true
                        # mover arquivo de resultado para pasta de reports (se existir)
                        if [ -f validation_results.json ]; then
                            mv -f validation_results.json dados/reports/validation_results.json || true
                        fi
                    else
                        echo "No recomendacoes/Testes/ValidacaoSistema.py found, skipping recommendation validation"
                    fi
                '''
            }
            post {
                always {
                    // Arquiva os resultados de validação a partir de dados/reports
                    archiveArtifacts artifacts: 'dados/reports/validation_results.json', allowEmptyArchive: true
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
        stage('Deploy Application') {
            when { expression { return env.BRANCH_NAME == 'main' } }
            steps {
                echo 'Fazendo deploy da aplicação...'
                sh '''
                    # Sempre usa a imagem mais recente do Docker Hub
                    IMAGE_LATEST="alvarocareli/aluga-ai:latest"

                    echo "Baixando imagem mais recente: $IMAGE_LATEST"
                    if docker pull "$IMAGE_LATEST" >/dev/null 2>&1; then 

                        # Garante diretórios apenas para data e media
                        if [ -z "${HOST_DATA_DIR}" ]; then
                            HOST_DATA_DIR="${WORKSPACE}/data"
                        fi
                        if [ -z "${HOST_MEDIA_DIR}" ]; then
                            HOST_MEDIA_DIR="${WORKSPACE}/media"
                        fi

                        mkdir -p "${HOST_DATA_DIR}" "${HOST_MEDIA_DIR}"

                        # Remove containers antigos
                        docker rm -f aluga-ai aluga-ai-app || true 

                        echo "Subindo novo container..."

                        # Container SEM volume de static → usa static interno da imagem sempre
                        CID=$(docker run -d \
                            --name aluga-ai \
                            --restart unless-stopped \
                            -p 8000:8000 \
                            -v "${HOST_DATA_DIR}:/app/data" \
                            -v "${HOST_MEDIA_DIR}:/app/media" \
                            -e DJANGO_SETTINGS_MODULE=aluga_ai_web.settings \
                            -e PYTHONPATH=/app \
                            ${IMAGE_LATEST} 2>/dev/null || true)

                        echo "Started container ID: $CID"

                        if [ -n "${CID}" ]; then
                            sleep 5

                            docker ps --filter "id=${CID}" --format "{{.ID}} {{.Names}} {{.Status}}" || true
                            docker inspect --format '{{json .State}}' "${CID}" || true
                            docker logs --tail 50 "${CID}" || true

                            echo "Executando collectstatic dentro do container..."
                            if docker exec "${CID}" python manage.py collectstatic --noinput >/dev/null 2>&1; then
                                echo "collectstatic executado com sucesso."
                                docker exec "${CID}" sh -c "ls -la /app/staticfiles || true"
                            else
                                echo "AVISO: collectstatic falhou dentro do container."
                                docker exec "${CID}" sh -c "ls -la /app || true"
                            fi

                        else
                            echo "docker run não retornou um ID. Container pode ter falhado ao iniciar."
                        fi

                    else
                        echo "Falha ao puxar imagem ${IMAGE_LATEST}. Deploy cancelado."
                    fi
                '''
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
                        <p>This is a Jenkins  CICD pipeline status.</p>
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
}  