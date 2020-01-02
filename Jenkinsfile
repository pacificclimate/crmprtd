@Library('pcic-pipeline-library')_


node {
    stage('Code Collection') {
        codeCollection()
    }

    stage('Testing') {
        parallel "Python 3.6": {
            test_with_container('crmprtd-python36')
        },
        "Python 3.7": {
            runPythonTestSuite('crmprtd-python37')
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
