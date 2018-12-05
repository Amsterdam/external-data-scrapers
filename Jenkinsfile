#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block();
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#junk-kanaal', color: 'danger'

        throw t;
    }
    finally {
        if (tearDown) {
            tearDown();
        }
    }
}


node {

    stage("Checkout") {
        checkout scm
    }

    stage('Test') {
        tryStep "test", {
            sh "api/deploy/test/test.sh &&" +
               "import/deploy/test/test.sh"
        }
    }

    stage("Build dockers") {
        tryStep "build", {
            def importer = docker.build("build.datapunt.amsterdam.nl:5000/external-data-scrapers_importer:${env.BUILD_NUMBER}", "scrape_api")
                importer.push()
                importer.push("acceptance")

            def api = docker.build("build.datapunt.amsterdam.nl:5000/external-data-scrapers:${env.BUILD_NUMBER}", "api")
                api.push()
                api.push("acceptance")
        }
    }
}
