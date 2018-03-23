#!groovy
node('docker')
{
    stage('Checkout')
    {
        checkout scm
    }

    stage('Build')
    {
        sh "docker build --tag jsonmodels:${env.BRANCH_NAME}.${env.BUILD_NUMBER} ."
    }
}
