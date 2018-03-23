#!groovy
node('docker')
{
    def imageTag = "stardust-193112/jsonmodels:${env.BRANCH_NAME}.${env.BUILD_NUMBER}"

    stage('Checkout')
    {
        checkout scm
    }

    stage('Build')
    {
        sh "docker build --tag ${imageTag} ."
    }
}
