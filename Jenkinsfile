pipeline {
  agent any

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
      steps { checkout scm }
    }

    stage("Unit Tests (pytest)") {
  agent {
    docker {
      image 'python:3.11'
      args '-u root:root'
    }
  }
  steps {
    sh '''
      python -m venv .venv
      . .venv/bin/activate
      pip install --upgrade pip
      pip install -r requirements.txt pytest
      pytest -q
    '''
  }
}

    stage("Build & Push Image to ECR") {
      steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-creds']]) {
          sh """
            set -eux
            GIT_SHA=\$(git rev-parse --short HEAD)
            IMAGE="${ECR_REPO_URL}:\${GIT_SHA}"

            aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO_URL}

            docker build -t "\$IMAGE" .
            docker push "\$IMAGE"

            echo "\$GIT_SHA" > image_tag.txt
          """
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