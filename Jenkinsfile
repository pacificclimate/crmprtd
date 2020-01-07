@Library('pcic-pipeline-library@fix-mistakes-2')_


node {
    stage('Code Collection') {
        codeCollection()
    }

    stage('Testing') {
        def requirements = ['requirements.txt', 'test_requirements.txt']
        def pypytestArgs = '-v --tb=short --cov --flake8'
        def options = [containerData: 'crmprtd']

        parallel "Python 3.5": {
            runPythonTestSuite('crmprtd-python35', requirements, pytestArgs, options)
        },
        "Python 3.6": {
            runPythonTestSuite('crmprtd-python36', requirements, pytestArgs, options)
        },
        "Python 3.7": {
            runPythonTestSuite('crmprtd-python37', requirements, pytestArgs, options)
        }
    }

    if (pypiPublishable()) {
        stage('Push to PYPI') {
            publishPythonPackage('crmprtd-python35', 'PCIC_PYPI_CREDS')
        }
    }

    stage('Clean Workspace') {
        cleanWs()
    }
}
