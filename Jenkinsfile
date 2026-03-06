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

    stage("Clean Workspace") {
  steps {
    deleteDir()
  }
}

    stage("Checkout") {
  steps {
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
  steps {
    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-creds']]) {
      sh '''
        set -eux
        IMAGE="${ECR_REPO_URL}:${IMAGE_TAG}"

        aws --version
        docker --version

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
      sh '''
        set -eux

        TAG=$(cat image_tag.txt)
        export TAG

        rm -rf /tmp/birds-gitops

        git clone https://${GIT_USER}:${GIT_TOKEN}@github.com/geetha1309/birds-gitops.git /tmp/birds-gitops
        cd /tmp/birds-gitops

        git checkout main

        git config user.email "geetha1309@users.noreply.github.com"
        git config user.name "geetha1309"

        python3 - <<PY
import os
import re
from pathlib import Path

tag = os.environ["TAG"]

path = Path("apps/birds/overlays/prod/kustomization.yaml")
text = path.read_text()

text = re.sub(r'newTag:\\s*"[^"]+"', f'newTag: "{tag}"', text)

path.write_text(text)
PY

        cat apps/birds/overlays/prod/kustomization.yaml

        git add apps/birds/overlays/prod/kustomization.yaml

        git commit -m "Deploy birds-app image tag $TAG" || true

        git push origin main
      '''
    }
  }
}
  }
}