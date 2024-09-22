#!/bin/bash

set -e

# Load environment variables
if [ -f .envrc ]; then
    source .envrc
else
    echo ".envrc file not found!"
    exit 1
fi

# Variables
IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:latest"

# Step 1: Authenticate Docker to your default ECR registry
echo "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

# Step 2: Create ECR repository if it doesn't exist
echo "Creating ECR repository if it doesn't exist..."
aws ecr describe-repositories --repository-names "$ECR_REPOSITORY_NAME" --region $AWS_REGION || aws ecr create-repository --repository-name "$ECR_REPOSITORY_NAME" --region $AWS_REGION

# Step 3: Build the Docker image
echo "Building Docker image..."
docker build -t "$ECR_REPOSITORY_NAME" .

# Step 4: Tag the Docker image
echo "Tagging Docker image..."
docker tag "$ECR_REPOSITORY_NAME":latest "$IMAGE_URI"

# Step 5: Push the Docker image to ECR
echo "Pushing Docker image to ECR..."
docker push "$IMAGE_URI"

# Step 6: Update the Lambda function to use the new ECR image
echo "Updating Lambda function..."
aws lambda update-function-code --function-name "$LAMBDA_FUNCTION_NAME" --image-uri "$IMAGE_URI" --region $AWS_REGION

echo "Deployment completed successfully."