pipeline {
    agent any

    stages {
        stage('Pre-Clean') {
            steps {
                echo 'Cleaning all Docker containers, images, and volumes'
                sh 'if [[ $(docker ps -q) ]]; then docker kill $(docker ps -q); fi'
                sh 'if [[ $(docker ps -q -a) ]]; then docker rm $(docker ps -q -a); fi'
                sh 'docker system prune --all --force'
            }
        }
        stage('Build') {
            steps {
                echo 'Building and installing Python wheel'
                sh 'python setup.py bdist_wheel sdist'
                sh 'pip install --user dist/nvidia_bobber-*.whl'
                echo 'Building the Bobber Docker image'
                sh 'bobber build'
                sh 'docker images | grep bobber'
            }
        }
        stage('Test') {
            steps {
                echo 'Running a two-node test to verify functionality'
                sh 'bobber cast /raid'
            }
        }
    }
}
