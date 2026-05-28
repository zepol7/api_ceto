pipeline {
    agent any

    environment {
        APP_NAME  = 'api-tareas'
        VERSION   = "1.0.${BUILD_NUMBER}"
        IMAGE_TAG = "${APP_NAME}:${VERSION}"
        PUERTO    = '5000'
        SONAR_URL = 'http://host.docker.internal:9000'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo "Branch: ${env.BRANCH_NAME} | Commit: ${env.GIT_COMMIT}"
            }
        }

        stage('Instalar y probar') {
            steps {
                bat '"C:\\Users\\helio.lopez_davinci\\AppData\\Local\\Python\\bin\\python.exe" -m pip install -r requirements.txt --quiet'
                bat '"C:\\Users\\helio.lopez_davinci\\AppData\\Local\\Python\\bin\\python.exe" -m pip install pytest pytest-cov flake8 --quiet'
                bat 'mkdir reports 2>nul || echo ok'
                bat 'flake8 app.py tests\\ --max-line-length=100'
                bat """
                    "C:\\Users\\helio.lopez_davinci\\AppData\\Local\\Python\\bin\\python.exe" -m pytest tests\\ -v ^
                      --junitxml=reports\\junit.xml ^
                      --cov=. ^
                      --cov-report=xml:reports\\coverage.xml ^
                      --cov-fail-under=75
                """
            }
            post {
                always { junit 'reports\\junit.xml' }
            }
        }

        stage('Analisis SonarQube') {
            steps {
                withSonarQubeEnv('SonarQube-Local') {
                    withSonarQubeInstallation('SonarQube-Scanner-5') {
                        bat """
                            sonar-scanner ^
                              -Dsonar.projectKey=%APP_NAME% ^
                              -Dsonar.sources=. ^
                              -Dsonar.exclusions=tests/**,venv/**,reports/** ^
                              -Dsonar.python.coverage.reportPaths=reports/coverage.xml ^
                              -Dsonar.host.url=%SONAR_URL%
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build imagen Docker') {
            steps {
                bat "docker build -t %IMAGE_TAG% ."
                bat "docker tag %IMAGE_TAG% %APP_NAME%:latest"
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                bat "docker stop %APP_NAME% 2>nul || echo ok"
                bat "docker rm %APP_NAME% 2>nul || echo ok"
                bat """
                    docker run -d ^
                      --name %APP_NAME% ^
                      --restart unless-stopped ^
                      -p %PUERTO%:%PUERTO% ^
                      %IMAGE_TAG%
                """
                bat 'timeout /t 5 /nobreak'
                bat "curl -f http://localhost:%PUERTO%/salud"
            }
        }
    }

    post {
        success { echo "Pipeline exitoso: v${env.VERSION} en puerto ${env.PUERTO}" }
        failure { echo "Pipeline fallido. Revisar SonarQube y reportes de prueba." }
        always  { cleanWs() }
    }
}