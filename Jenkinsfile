@Library('pcic-pipeline-library')_


node {
    stage('Code Collection') {
        cleanWs()
        codeCollection()
    }

    stage('Testing') {
        def requirements = ['requirements.txt', 'test_requirements.txt']
        def testArgs = '-v --tb=short --cov --flake8'
        def optParams = [containerData: 'crmprtd']

        parallel "Python 3.5": {
            runPythonTestSuite('crmprtd-python35', requirements, testArgs, optParams)
        },
        "Python 3.6": {
            runPythonTestSuite('crmprtd-python36', requirements, testArgs, optParams)
        },
        "Python 3.7": {
            runPythonTestSuite('crmprtd-python37', requirements, testArgs, optParams)
        }
    }

    String tag = sh (script: 'git tag --contains', returnStdout: true).trim()

    if (publishable()) {
        stage('Push to PYPI') {
            publishPythonPackage('crmprtd-python35', 'PCIC_PYPI_CREDS')
        }
    }

    stage('Clean Workspace') {
        cleanWs()
    }
}
