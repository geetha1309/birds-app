pipeline {
  
  agent any
  options {
  skipDefaultCheckout(true)
}

  environment {
    AWS_REGION = "eu-west-1"

    // CHANGE THIS to your ECR repo URL from terraform output:
    ECR_REPO_URL = "636362695216.dkr.ecr.eu-west-1.amazonaws.com/birds-app"

    // CHANGE THIS to your GitOps repo URL:
    GITOPS_REPO  = "https://github.com/geetha1309/birds-gitops.git"
    GITOPS_BRANCH = "main"

    IMAGE_NAME_IN_KUSTOMIZE = "REPLACED_BY_KUSTOMIZE"
  }

  stages {
    stage("Checkout") {
  steps {
    deleteDir()          // wipes workspace even if Jenkins UI didn’t
    checkout scm         // uses the SCM config from the job
  }
}

  stage("Compute Image Tag") {
  steps {
    script {
      env.IMAGE_TAG = sh(
        script: "git rev-parse --short HEAD",
        returnStdout: true
      ).trim()
      echo "IMAGE_TAG=${env.IMAGE_TAG}"
    }
  }
}

    stage("Unit Tests (pytest)") {
  agent {
    docker {
      image 'python:3.12'
      args '-u root:root'
    }
  }
  steps {
    sh '''
      python -m venv .venv
      . .venv/bin/activate
      pip install --upgrade pip
      pip install -r requirements.txt pytest httpx

      export PYTHONPATH=$PYTHONPATH:$(pwd)

      pytest -q
    '''
  }
}

    stage("Build & Push Image to ECR") {
  agent {
    docker {
      image 'amazon/aws-cli:2.17.0'
      args "--entrypoint='' -u root:root -v /var/run/docker.sock:/var/run/docker.sock"
    }
  }
  steps {
    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-creds']]) {
      sh '''
        set -eux
        IMAGE="${ECR_REPO_URL}:${IMAGE_TAG}"

        aws --version
        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO_URL}

        docker build -t "$IMAGE" .
        docker push "$IMAGE"

        echo "${IMAGE_TAG}" > image_tag.txt
      '''
    }
  }
}

    stage("Update GitOps repo image tag") {
      steps {
        withCredentials([usernamePassword(credentialsId: 'gitops-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
          sh """
            set -eux
            TAG=\$(cat image_tag.txt)

            rm -rf /tmp/birds-gitops
            git clone https://\${GIT_USER}:\${GIT_TOKEN}@${GITOPS_REPO.replace('https://','')} /tmp/birds-gitops
            cd /tmp/birds-gitops
            git checkout ${GITOPS_BRANCH}

            perl -0777 -i -pe 's/(newTag:\\s*\\")([^\"]+)(\\")/\\1'"\$TAG"'\\3/g' apps/birds/overlays/prod/kustomization.yaml

            git add apps/birds/overlays/prod/kustomization.yaml
            git commit -m "Deploy birds-app image tag \$TAG" || true
            git push origin ${GITOPS_BRANCH}
          """
        }
      }
    }
  }
}