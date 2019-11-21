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
            sh 'pip install -r requirements.txt -r test_requirements.txt -i http://tools.pacificclimate.org/pypiserver/ --trusted-host tools.pacificclimate.org'
            sh 'pip install .'

            // Tests
            sh 'py.test -v --tb=short --cov --flake8'
        }
    }
}


def build_release_package() {
    withDockerServer([uri: PCIC_DOCKER]) {
        def pytainer = docker.image('crmprtd-python35')

        pytainer.inside {
            // get twine
            sh 'pip install twine'

            // Build
            sh 'python setup.py sdist'

            withCredentials([usernamePassword(credentialsId: 'PCIC_PYPI_CREDS', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                // Release
                sh "twine upload --repository-url https://pypi.pacificclimate.org/simple/ -u $USERNAME -p $PASSWORD dist/*"
            }

        }
    }
}


node {
    stage('Code Collection') {
        // checkout scm
        git(url: 'https://github.com/pacificclimate/crmprtd.git')
    }

    stage('Testing') {
        parallel "Python 3.5": {
            test_with_container('crmprtd-python35')
        },
        "Python 3.6": {
            test_with_container('crmprtd-python36')
        },
        "Python 3.7": {
            test_with_container('crmprtd-python37')
        }
    }

    stage('Build Package') {
        build_release_package()
    }

    stage('Clean Workspace') {
        cleanWs()
    }
}
