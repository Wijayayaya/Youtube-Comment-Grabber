pipeline {
    agent none

    options {
        disableConcurrentBuilds()
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '5'))
    }

    environment {
        APP_NAME = 'youtube_chat_dashboard'
        VENV_DIR = '.venv_ci'
        ARTIFACT = "${APP_NAME}-${BUILD_NUMBER}.tar.gz"
        DEPLOY_ROOT = '/var/www/youtube_chat_dashboard'
    }

    stages {
        stage('Checkout') {
            agent { label 'controller' }
            steps {
                checkout scm
                stash name: 'source', includes: '**', excludes: '.git/**, .venv/**, venv/**, __pycache__/**, runtime/**'
            }
        }

        stage('Install & Test') {
            agent { label 'controller' }
            steps {
                unstash 'source'
                sh '''
                    set -e

                    python3 -m venv ${VENV_DIR} || true
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt

                    # Run migrations and tests (tests allowed to fail without breaking pipeline)
                    python manage.py migrate --noinput || true
                    python manage.py test --verbosity=2 || true
                '''
            }
        }

        stage('Package Artifact') {
            agent { label 'controller' }
            steps {
                sh '''
                    set -e
                    tar czf ${ARTIFACT} \
                        manage.py \
                        requirements.txt \
                        README.md \
                        comments \
                        dashboard \
                        templates \
                        static
                '''
                stash name: 'artifact', includes: "${ARTIFACT}"
                archiveArtifacts artifacts: "${ARTIFACT}", fingerprint: true
            }
        }

        stage('Deploy to Production') {
            when { branch 'main' }
            agent { label 'prod' }
            steps {
                unstash 'artifact'
                sh '''
                    set -e

                    SERVICE_WEB=dashboardLive
                    SERVICE_POLL=pollLive
                    DEPLOY_ROOT="${DEPLOY_ROOT}"
                    RELEASES_DIR="$DEPLOY_ROOT/releases"
                    CURRENT_LINK="$DEPLOY_ROOT/current"

                    mkdir -p "$RELEASES_DIR"

                    RELEASE_DIR="$RELEASES_DIR/${APP_NAME}-${BUILD_NUMBER}"

                    sudo -n systemctl stop "$SERVICE_WEB" "$SERVICE_POLL" || true

                    rm -rf "$RELEASE_DIR"
                    mkdir -p "$RELEASE_DIR"
                    tar xzf "${ARTIFACT}" -C "$RELEASE_DIR"

                    python3 -m venv "$RELEASE_DIR/.venv"
                    . "$RELEASE_DIR/.venv/bin/activate"
                    pip install --upgrade pip
                    pip install -r "$RELEASE_DIR/requirements.txt"

                    # Run migrations and collectstatic if applicable
                    cd "$RELEASE_DIR"
                    python manage.py migrate --noinput
                    python manage.py collectstatic --noinput

                    sudo -n chown -R www-data:www-data "$RELEASE_DIR"
                    ln -sfn "$RELEASE_DIR" "$CURRENT_LINK"

                    sudo -n systemctl daemon-reload || true
                    sudo -n systemctl restart "$SERVICE_WEB" "$SERVICE_POLL"
                    sudo -n systemctl is-active --quiet "$SERVICE_WEB"
                    sudo -n systemctl is-active --quiet "$SERVICE_POLL"

                    cd "$RELEASES_DIR"
                    OLD_RELEASES=$(ls -1dt "${APP_NAME}"-* 2>/dev/null | tail -n +6 || true)
                    if [ -n "$OLD_RELEASES" ]; then
                        echo "Menghapus release lama:"
                        echo "$OLD_RELEASES" | tr ' ' '\n'
                        echo "$OLD_RELEASES" | xargs -r sudo -n rm -rf -- || true
                    fi
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished'
        }
    }
}
