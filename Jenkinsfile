pipeline {
    options { disableConcurrentBuilds() }
    agent { label 'docker' }
    parameters {
        credentials credentialType: 'com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey', defaultValue: 'kayobe-ssh-private-key', description: 'Kayobe SSH Key', name: 'KAYOBE_SSH_CREDS', required: true
        credentials credentialType: 'org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl', defaultValue: 'kayobe-vault-password', description: 'Kayobe Ansible Vault Password', name: 'KAYOBE_VAULT_PASSWORD', required: true
        string defaultValue: 'http://localhost:4000/', description: 'Docker Registry to push images to', name: 'DOCKER_REGISTRY', trim: true
        string description: 'Command to run in docker container', name: 'COMMAND', trim: false
        credentials credentialType: 'org.jenkinsci.plugins.plaincredentials.impl.FileCredentialsImpl', description: 'Kayobe SSH Config file', name: 'KAYOBE_SSH_CONFIG', required: false
    }
    environment {
        REGISTRY = "${params.DOCKER_REGISTRY}"
        KAYOBE_IMAGE = "${currentBuild.projectName}:${env.GIT_COMMIT}"
    }

    stages {
        // Do parameter validation in a stage so that the git checkout of the pipeline still works.
        // This is necessary to update the build parameters.
        stage('Validate parameters') {
            steps {
                script {
                    if (!params.COMMAND){
                        // Fail early
                        error("You must set the COMMAND parameter")
                    }
                }
            }
        }
        stage('Build and Push') {
            steps {
                script {
                    def kayobeImage = docker.build("$KAYOBE_IMAGE")
                    docker.withRegistry("$REGISTRY") {
                        kayobeImage.push()
                        kayobeImage.push('latest')
                    }
                }
            }
        }
        stage('Deploy') {
            stages {
                stage('Prepare Secrets') {
                    environment {
                        KAYOBE_VAULT_PASSWORD = credentials("${params.KAYOBE_VAULT_PASSWORD}")
                        KAYOBE_SSH_CREDS_FILE = credentials("${params.KAYOBE_SSH_CREDS}")
                    }
                    steps {
                        sh 'mkdir -p secrets/.ssh'
                        sh "cp $KAYOBE_SSH_CREDS_FILE secrets/.ssh/id_rsa"
                        sh(returnStdout: false, script: 'ssh-keygen -y -f secrets/.ssh/id_rsa > secrets/.ssh/id_rsa.pub')
                        sh(returnStdout: false, script: 'echo $KAYOBE_VAULT_PASSWORD > secrets/vault.pass')
                    }
                }
                stage('Optionally prepare SSH Config') {
                    when {
                        expression { params.KAYOBE_SSH_CONFIG != null && params.KAYOBE_SSH_CONFIG != '' }
                    }
                    environment {
                        KAYOBE_SSH_CONFIG_FILE = credentials("${params.KAYOBE_SSH_CONFIG}")
                    }
                    steps {
                        sh "cp $KAYOBE_SSH_CONFIG_FILE secrets/.ssh/config"
                    }
                }
                stage('Run Kayobe') {
                    agent {
                        docker {
                            image "$KAYOBE_IMAGE"
                            registryUrl "$REGISTRY"
                            reuseNode true
                        }
                    }
                    environment {
                        KAYOBE_VAULT_PASSWORD = credentials("${params.KAYOBE_VAULT_PASSWORD}")
                    }
                    steps {
                        sh 'cp -R secrets/. /secrets'
                        sh '/bin/entrypoint.sh echo READY'
                        sh 'kayobe control host bootstrap'
                        sh "${params.COMMAND}"
                    }
                }
            }
        }
    }
    post {
        cleanup {
            dir('secrets') {
                deleteDir()
            }
        }
   }
}
