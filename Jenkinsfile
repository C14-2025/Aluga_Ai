pipeline {
    agent {
        docker {
            image 'alugaai-app'
            args '-p 8000:8000 -w /app'
        }p
    }
    environment {
        DJANGO_SETTINGS_MODULE = 'aluga_ai_web.settings'
        PYTHONPATH = "${env.WORKSPACE}"
        PYTHON_VERSION = '3.13'
    }
    stages {
        stage('Checkout') {
            steps {
                // ensure the repository is checked out into the Jenkins workspace
                checkout scm
                // copy workspace contents into /app so runtime container has the project files
                // this makes the job resilient to the Docker agent's working-dir behavior
                sh 'echo "Copying workspace to /app (if present)..."'
                sh 'cp -a "$WORKSPACE/." /app/ || true'
                // debug: show what files are present in the workspace inside the container
                sh 'pwd'
                sh 'ls -la'
                sh 'echo "WORKSPACE=$WORKSPACE"'
                sh 'ls -la "$WORKSPACE" || true'
            }
        }
        stage('Preparar Ambiente') {
            steps {
                sh 'pwd'
                sh 'ls -l'
                sh 'ls -l requirements.txt || echo "requirements.txt não encontrado"'
                sh 'python --version'
                sh 'python -m pip install --upgrade pip'
                sh 'python manage.py migrate'
                dir('aluga_ai_web') {
                    sh 'pytest BancoDeDados/test_bd.py --template=html1/index.html --report=report_bd.html'
                }
                archiveArtifacts artifacts: 'aluga_ai_web/report_bd.html', onlyIfSuccessful: true
            }
        }
        stage('Testes Unitários de Bd') {
            steps {
                sh 'python manage.py migrate'
                dir('aluga_ai_web') {
                    sh 'pytest BancoDeDados/test_bd.py --template=html1/index.html --report=report_bd.html'
                }
                archiveArtifacts artifacts: 'aluga_ai_web/report_bd.html', onlyIfSuccessful: true
            }
        }
        stage('Testes de ETL') {
            steps {
                sh 'python manage.py migrate'
                dir('aluga_ai_web/Dados') {
                    sh 'pytest test_etl.py --template=html1/index.html --report=report_etl.html'
                    sh 'python etl.py'
                }
                archiveArtifacts artifacts: 'aluga_ai_web/Dados/report_etl.html', onlyIfSuccessful: true
            }
        }
        stage('Rodar Servidor Django') {
            steps {
                sh 'python manage.py migrate --noinput'
                sh 'nohup python manage.py runserver 0.0.0.0:8000 &'
                sh 'sleep 10'
                sh 'curl -I http://127.0.0.1:8000 || echo "Servidor não respondeu."'
                sh 'python manage.py test'
            }
        }
        stage('Notificação por email') {
            when {
                expression { return env.NOTIFY_EMAIL != null }
            }
            steps {
                mail to: "${env.NOTIFY_EMAIL}", subject: 'Status da Pipeline', body: 'Pipeline executada.'
            }
        }
    }
    post {
        always {
            echo 'Pipeline finalizada.'
        }
    }
}