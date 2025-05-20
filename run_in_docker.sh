#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default image parameters
DEFAULT_IMAGE_NAME="coding-agent-python"
DEFAULT_USERNAME=""
DEFAULT_TAG="latest"
BUILD_LOCALLY=true

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --pull)
      BUILD_LOCALLY=false
      shift
      ;;
    --username)
      DEFAULT_USERNAME="$2"
      shift 2
      ;;
    --tag)
      DEFAULT_TAG="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--pull] [--username DOCKERHUB_USERNAME] [--tag TAG]"
      exit 1
      ;;
  esac
done

# Define the image name
if [ -z "$DEFAULT_USERNAME" ]; then
  IMAGE_NAME="$DEFAULT_IMAGE_NAME:$DEFAULT_TAG"
else
  IMAGE_NAME="$DEFAULT_USERNAME/$DEFAULT_IMAGE_NAME:$DEFAULT_TAG"
fi

# Either build locally or pull from Docker Hub
if [ "$BUILD_LOCALLY" = true ]; then
  echo "Building Docker image $IMAGE_NAME from $SCRIPT_DIR..."
  docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"
  
  # Check if build was successful
  if [ $? -ne 0 ]; then
    echo "Error: Docker build failed"
    exit 1
  fi
else
  echo "Pulling Docker image $IMAGE_NAME from Docker Hub..."
  docker pull "$IMAGE_NAME"
  
  # Check if pull was successful
  if [ $? -ne 0 ]; then
    echo "Error: Failed to pull image $IMAGE_NAME from Docker Hub"
    exit 1
  fi
fi

# Check if .env file exists. If not, check for ANTHROPIC_API_KEY environment variable
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo ""
    echo "WARNING: .env file not found in $SCRIPT_DIR."
    
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        echo "The agent will not work correctly without an ANTHROPIC_API_KEY."
        echo "Please provide your API key: "
        read -s API_KEY
        if [ -z "$API_KEY" ]; then
            echo "No API key provided. Exiting."
            exit 1
        fi
        ENV_VARS="-e ANTHROPIC_API_KEY=$API_KEY"
    else
        echo "Using ANTHROPIC_API_KEY from environment variables."
        ENV_VARS="-e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY"
    fi
else
    ENV_VARS="--env-file $SCRIPT_DIR/.env"
fi

echo ""
echo "Running Docker image $IMAGE_NAME..."
echo "Host directory '$SCRIPT_DIR' will be mounted to '/workspace' in the container."
echo "To interact with files on your host machine, refer to them via '/workspace/your_file_or_dir' when talking to the agent."
echo "The agent's own code is in /app within the container. Its current working directory upon start is /workspace."
echo "Press Ctrl+C to stop the agent."

# Run the Docker container
docker run -it --rm \
  -v "$SCRIPT_DIR:/workspace" \
  $ENV_VARS \
  "$IMAGE_NAME"