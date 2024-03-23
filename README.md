# Django Project Deployment with Docker and Kubernetes

This repository contains a Django project intended for deployment using Docker containers orchestrated with Kubernetes.

## Prerequisites

Before deploying this Django project, ensure the following dependencies are installed:

- Docker
- Kubernetes
- kubectl

## Deployment Steps

Follow these steps to deploy the Django project using Docker and Kubernetes:

1. **Clone Repository**: Clone this repository to your local machine.
   ```bash
   git clone https://github.com/asifxohd/kubernetes.git
   
2. ## create shoecart-secret.yaml file
   ```yaml
      apiVersion: v1
      kind: Secret
      metadata:
        name: shoecart-secret
      type: Opaque
      data:
        SECRET_KEY: 
        EMAIL_HOST_USER: 
        EMAIL_HOST_PASSWORD: 
        RAZORPAY_API_KEY: 
        RAZORPAY_API_SECRET_KEY: 
        POSTGRES_DB: 
        POSTGRES_USER: 
        POSTGRES_PASSWORD: 
        POSTGRES_HOST:
3. ## create .env file
   ```.env
      SECRET_KEY=
      EMAIL_HOST_USER=
      EMAIL_HOST_PASSWORD=
      RAZORPAY_API_KEY=
      RAZORPAY_API_SECRET_KEY=
      POSTGRES_NAME=
      POSTGRES_USER=
      POSTGRES_PASSWORD=
      POSTGRES_HOST=

4. ## Docker image
   ```
      docker build -t <image_name> .
      docker run -p 8000:8000 <image_name>

5. ## Deployment with Kuberneties
   ```
      kubctl apply -f <kuberneties file directory>

happy coding 
