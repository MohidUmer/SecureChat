pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Building..'
                // Here you can define commands for your build
                // Example: bat 'mvn clean package' (for Windows)
            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
                // Here you can define commands for your tests
                // Example: bat 'mvn test'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
                // Here you can define commands for your deployment
            }
        }
    }
}
