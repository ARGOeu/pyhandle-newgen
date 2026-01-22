pipeline {
    agent any
    options {
        checkoutToSubdirectory('pyhandle-newgen')
    }
    environment {
        PROJECT_DIR = 'pyhandle-newgen'
        GIT_COMMIT = sh(script: "cd ${WORKSPACE}/$PROJECT_DIR && git log -1 --format=\"%H\"", returnStdout: true).trim()
        GIT_COMMIT_HASH = sh(script: "cd ${WORKSPACE}/$PROJECT_DIR && git log -1 --format=\"%H\" | cut -c1-7", returnStdout: true).trim()
        GIT_COMMIT_DATE = sh(script: "date -d \"\$(cd ${WORKSPACE}/$PROJECT_DIR && git show -s --format = %ci ${GIT_COMMIT_HASH})\" \"+%Y%m%d%H%M%S\"", returnStdout: true).trim()
    }
    stages {
        stage('Run Linting') {
            agent {
                docker {
                    image 'argo.registry:5000/epel-9-acc'
                    args '-u jenkins:jenkins'
                }
            }
            steps {
                echo 'Executing lint checks'
                sh '''
                    cd ${WORKSPACE}/$PROJECT_DIR
                    rm -f .python-version &>/dev/null
                    rm -rf .coverage* .tox/ coverage.xml &> /dev/null

                    pip install flake8 isort bandit mypy

                    export PATH=$HOME/.local/bin:$PATH

                    echo "Running flake8..."
                    flake8 --max-line-length=120 .

                    echo "Running isort..."
                    isort --check-only .

                    echo "Running bandit..."
                    bandit -r .

                    echo "Running mypy..."
                    if find . -name "*.py" | grep -q .; then
                        mypy --disable-error-code=import-untyped --ignore-missing-imports .
                    else
                        echo "No Python files found. Skipping mypy."
                    fi
                '''
            }
        }
        stage('Run tests') {
            agent {
                docker {
                    image 'argo.registry:5000/epel-9-acc'
                    args '-u jenkins:jenkins'
                }
            }
            steps {
                echo 'Executing tox tests'
                sh '''
                    cd ${WORKSPACE}/$PROJECT_DIR
                    rm -f .python-version &>/dev/null
                    rm -rf .coverage* .tox/ coverage.xml &> /dev/null
                    source $HOME/pyenv.sh
                    ALLPYVERS=$(pyenv versions | grep '^[ ]*[0-9]' | tr '\n' ' ')
                    echo Found Python versions $ALLPYVERS
                    pyenv local $ALLPYVERS
                    export TOX_SKIP_ENV="py27.*|py36.*"
                    if [ -f tox.ini ] || [ -f pyproject.toml ] || [ -f setup.cfg ]; then
                        echo "Running tox..."
                        tox -p all
                        coverage xml --omit=*usr* --omit=*.tox*
                    else
                    echo "No tox config found. Skipping tox."
                    fi
                    '''
            }
        }
    }
    post {
        always {
            echo 'Cleaning workspace and exiting'
            cleanWs()
        }
    }
}