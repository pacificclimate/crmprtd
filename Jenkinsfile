/**
 * Factored out common process for running test suite in python container
 *
 * @param pyimage Custom python image
 */
def test_with_container(String pyimage) {
    withDockerServer([uri: PCIC_DOCKER]) {
        def pytainer = docker.image(pyimage)

        pytainer.inside {
            // Installs
            withEnv(['PIP_INDEX_URL=https://pypi.pacificclimate.org/simple']) {
                sh 'pip install -r requirements.txt -r test_requirements.txt'
                sh 'pip install .'
            }

            // Tests
            sh 'py.test -v --tb=short --cov --flake8'
        }
    }
}


/**
 * Build and release package to pypi
 */
def push_to_pypi() {
    withDockerServer([uri: PCIC_DOCKER]) {
        def pytainer = docker.image('crmprtd-python35')

        pytainer.inside {
            // get twine
            sh 'pip install twine wheel'

            // Build
            sh 'python setup.py sdist bdist_wheel'

            // Release
            withCredentials([usernamePassword(credentialsId: 'PCIC_PYPI_CREDS', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                sh "twine upload --repository-url https://pypi.pacificclimate.org/ --skip-existing -u $USERNAME -p $PASSWORD dist/*"
            }
        }
    }
}


node {
    stage('Code Collection') {
        // The default checkout procedure runs with `git fetch --no-tags` so we
        // perform an additional fetch to gather the tags.
        checkout scm
        sh 'git fetch'
    }

    stage('Testing') {
        parallel "Python 3.6": {
            test_with_container('crmprtd-python36')
        },
        "Python 3.7": {
            test_with_container('crmprtd-python37')
        }
    }

    String tag = sh (script: 'git tag --contains', returnStdout: true).trim()

    if (BRANCH_NAME == 'master' && !tag.isEmpty()) {
        stage('Push to PYPI') {
            push_to_pypi()
        }
    }

    stage('Clean Workspace') {
        cleanWs()
    }
}
