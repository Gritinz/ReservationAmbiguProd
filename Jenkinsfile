// Jenkinsfile pour le projet de réservation de restaurant
pipeline {
    agent any
    environment {
        // Variables d'environnement pour Supabase et Django
        DB_NAME = credentials('DB_NAME')
        DB_USER = credentials('DB_USER')
        DB_PASSWORD = credentials('DB_PASSWORD')
        DB_HOST = credentials('DB_HOST')
        DB_PORT = credentials('DB_PORT')
        SECRET_KEY = credentials('SECRET_KEY')
    }
    stages {
        stage('Checkout') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'forge-credentials', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
                    git url: 'https://forge.univ-lyon1.fr/p2304161/reservationambigu.git', branch: 'master', credentialsId: 'forge-credentials'
                }
            }
        }
        stage('Setup Backend Environment') {
            steps {
                dir('restaurant_back') {
                    // Crée un environnement virtuel dans l'espace de travail
                    bat 'python -m venv venv'
                    // Active l'environnement virtuel et installe les dépendances
                    bat 'call venv\\Scripts\\activate && pip install -r requirements.txt'
                }
            }
        }
        stage('Run Backend Tests') {
            steps {
                dir('restaurant_back') {
                    bat 'call venv\\Scripts\\activate && python manage.py test'
                }
            }
        }
        stage('Install Frontend Dependencies') {
            steps {
                dir('restaurant_front') {
                    bat 'npm install'
                }
            }
        }
        stage('Run Frontend Build') {
            steps {
                dir('restaurant_front') {
                    bat 'npm run build'
                }
            }
        }
    }
}