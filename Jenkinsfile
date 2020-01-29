@Library('pcic-pipeline-library')_


node {
    stage('Code Collection') {
        collectCode()
    }

    stage('Testing') {
        def requirements = ['requirements.txt', 'test_requirements.txt']
        def pytestArgs = '-v --tb=short --cov --flake8'
        def options = [containerData: 'crmprtd']

        parallel "Python 3.6": {
            runPythonTestSuite('crmprtd-test36', requirements, pytestArgs, options)
        },
        "Python 3.7": {
            runPythonTestSuite('crmprtd-test37', requirements, pytestArgs, options)
        }
    }

    if (isPypiPublishable()) {
        stage('Push to PYPI') {
            publishPythonPackage('crmprtd-python35', 'PCIC_PYPI_CREDS')
        }
    }

    stage('Clean Workspace') {
        cleanWs()
    }
}
