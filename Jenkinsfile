/**
 * Factored out common process for running test suite in python container
 *
 * @param pyimage Custom python image
 */
def test_with_container(String pyimage) {
    withDockerServer([uri: PCIC_DOCKER]) {
        def pytainer = docker.image(pyimage)

        pytainer.inside() {
            // sanity checks
            sh 'which python'
            sh 'python --version'


            // try using pyenv plugin
            // withPythonEnv('/usr/local/bin/python') {
            //     sh 'pip install -r requirements.txt -r test_requirements.txt -i http://tools.pacificclimate.org/pypiserver/ --trusted-host tools.pacificclimate.org'
            //     sh 'pip install .'
            //     sh 'py.test -v --tb=short --cov --flake8'
            // }

            // // check for virtual env
            // if (!fileExists('.pyenv')) {
            //     // make one if we don't have one
            //     sh 'python3 -m venv .pyenv'
            // }
            //
            // // Installs in pyenv
            // sh '''. .pyenv/bin/activate
            // pip install --upgrade pip
            // pip install -r requirements.txt -r test_requirements.txt -i http://tools.pacificclimate.org/pypiserver/ --trusted-host tools.pacificclimate.org
            // pip install .
            // '''
            //
            // // Test suite in pyenv
            // sh '''. .pyenv/bin/activate
            // py.test -v --tb=short --cov --flake8
            // '''

            // Installs
            // sh 'apt-get update'
            // sh 'apt-get install -y postgresql postgis'
            sh 'pip install -r requirements.txt -r test_requirements.txt -i http://tools.pacificclimate.org/pypiserver/ --trusted-host tools.pacificclimate.org'
            sh 'pip install .'

            // Tests
            sh 'py.test -v --tb=short --cov --flake8'
        }
    }
}


node {
    stage('Code Collection') {
        cleanWs()
        checkout scm
    }

    stage('Testing') {
        parallel "Python 3.5": {
            test_with_container('crmprtd-tests-python35')
            // test_with_container('python:3.5')
        }
        // },
        // "Python 3.6": {
        //     test_with_container('python:3.6')
        // },
        // "Python 3.7": {
        //     test_with_container('python:3.7')
        // }
    }

    stage('Clean Workspace') {
        cleanWs()
    }
}
