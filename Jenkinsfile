def cluster = "flask-up"
def launch_type = "EC2"
def cluster_profile = "flask-up-profile"
def instance_type = "t2-medium"
def number_of_instances = "1"
def keypair = "cli"
def sg_group = "sg-08f2cb39ae5bdcde9"
def vpc = "vpc-07f3c76f"
pipeline {
    environment {
        registryCredential = 'jenkins_user_in_aws'
        registry_master = "746738551514.dkr.ecr.eu-west-2.amazonaws.com/flask-main" 
        registry_slave = "746738551514.dkr.ecr.eu-west-2.amazonaws.com/flask-slave" 
        //registryCredential = 'dockerhub_id' 
        dockerImageMaster = "${registry_master}:$BUILD_NUMBER"  
        dockerImageSlave = "${registry_slave}:$BUILD_NUMBER" 

    }
    agent any
    stages {
        stage('Git clone') {
            steps {
                git branch: 'main', credentialsId: 'github_user', url: 'https://github.com/tomcoh5/flask-time-manipulation'
            }
        } 
        stage('Building dockerfiles') {
            steps {
                echo "Building docker images"
                dir ("flask"){
                    script {
                        dockerImageMaster = docker.build registry_master + ":$BUILD_NUMBER" 
                    }
                }
                dir ("flask-slave") {
                    script {
                        dockerImageSlave = docker.build registry_slave + ":$BUILD_NUMBER" 
                    }
                }
            }
        }
        stage('Build Test pipeline') {
            steps {
                echo "Starting Docker-compose"
                sh 'env > .env'
                sh 'docker-compose up -d'
                echo "sleep for 10 seconds (waiting untill docker containers are built)"
                sh 'sleep 10'
            }
        }
        stage ('Testing Connection to websites') {
            steps {
                echo "Testing connection for flask-main"
                sh 'curl localhost:5000'
                echo "Testing connection for flask-slave"
                sh 'curl localhost:5001'
                echo "Test completed"
            }
        } 
        stage('Uploading to ECR (AWS)') {
            steps {
                script{
                    docker.withRegistry("https://" + registry_master, "ecr:eu-west-2:" + registryCredential) {
                        dockerImageMaster.push()
                    }
                    docker.withRegistry("https://" + registry_slave, "ecr:eu-west-2:" + registryCredential) {
                        dockerImageSlave.push()
                    }
                }
            }
        }
        stage ("Deployment to ECS (AWS)") {
            steps {
                sh  """ecs-cli up --force  --keypair ${keypair}  --capability-iam --size ${number_of_instances} --instance-type t2.medium --cluster-config ${cluster}  --ecs-profile ${cluster_profile} --security-group ${sg_group} --vpc ${vpc} --subnets subnet-73bac009,subnet-c3e26a8f """
                sh "sleep 60"
                sh """ ecs-cli compose up --create-log-groups --cluster-config ${cluster} --ecs-profile ${cluster_profile} """
            }
        }
    }
    post {
        always {
            sh 'docker-compose down'
            sh "docker rmi $registry_slave:$BUILD_NUMBER"
            sh "docker rmi $registry_master:$BUILD_NUMBER"
        }
    }
}
