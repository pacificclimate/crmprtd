node {
    withDockerServer([uri: PCIC_DOCKER]) {
        // Use image with gdal already installed
        def pyenv = docker.image('python:3.5')

        pyenv.inside('-u root') {
            stage('Install Requirements') {
                sh 'pip install -r requirements.txt -r test_requirements.txt -i http://tools.pacificclimate.org/pypiserver/ --trusted-host tools.pacificclimate.org'
                sh 'pip install .'
                sh 'apt-get install postgresql postgis'
            }

            stage('Test Suite') {
                sh 'py.test -v tests'
            }
        }
    }

    stage('Clean Workspace') {
        cleanWs()
    }
}
