#!/bin/bash

# Script to build and publish the Docker image to Docker Hub

# Default Docker Hub username or organization
DEFAULT_USERNAME="your-dockerhub-username"
DEFAULT_TAG="latest"

# Get Docker Hub username from argument or use default
if [ -z "$1" ]; then
  echo "No Docker Hub username provided, using default: $DEFAULT_USERNAME"
  USERNAME=$DEFAULT_USERNAME
else
  USERNAME=$1
fi

# Get tag from argument or use default
if [ -z "$2" ]; then
  echo "No tag provided, using default: $DEFAULT_TAG"
  TAG=$DEFAULT_TAG
else
  TAG=$2
fi

# Full image name
IMAGE_NAME="$USERNAME/coding-agent-python:$TAG"

# Build the Docker image
echo "Building Docker image: $IMAGE_NAME"
docker build -t "$IMAGE_NAME" .

# Check if build was successful
if [ $? -ne 0 ]; then
  echo "Error: Docker build failed"
  exit 1
fi

# Ask for confirmation before pushing
read -p "Do you want to push $IMAGE_NAME to Docker Hub? (y/n): " CONFIRM
if [[ $CONFIRM =~ ^[Yy]$ ]]; then
  echo "Pushing $IMAGE_NAME to Docker Hub..."
  
  # Check if user is logged in to Docker Hub
  docker info 2>&1 | grep "Username:" > /dev/null
  if [ $? -ne 0 ]; then
    echo "You are not logged in to Docker Hub. Please login:"
    docker login
    
    # Check if login was successful
    if [ $? -ne 0 ]; then
      echo "Error: Docker login failed"
      exit 1
    fi
  fi
  
  # Push the image to Docker Hub
  docker push "$IMAGE_NAME"
  
  if [ $? -eq 0 ]; then
    echo "Successfully pushed $IMAGE_NAME to Docker Hub"
    echo ""
    echo "Users can now pull and run your image with:"
    echo "docker run -it --rm -v \"\$(pwd):/workspace\" --env ANTHROPIC_API_KEY=\"your_api_key_here\" $IMAGE_NAME"
  else
    echo "Error: Failed to push image to Docker Hub"
    exit 1
  fi
else
  echo "Push canceled."
fi