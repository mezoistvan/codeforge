# Python Coding Agent

A CLI-based AI coding agent powered by Anthropic's Claude models, translated from an original Ruby project. This agent can understand instructions and use a set of tools to interact with your file system, such as reading files, listing files, editing files, and running shell commands (with user confirmation).

## Prerequisites

*   Python 3.8 or higher
*   An Anthropic API Key

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd coding_agent_python
    ```

2.  **Set up your Anthropic API Key:**
    Create a `.env` file in the `coding_agent_python` project root directory. Add your Anthropic API key to this file:
    ```env
    ANTHROPIC_API_KEY="your_anthropic_api_key_here"
    ```
    You can also set an optional `ANTHROPIC_DEFAULT_MODEL` if you wish to use a different Claude model than the default (`claude-3-sonnet-20240229`).

3.  **Install dependencies:**
    It's recommended to use a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
    Then install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To start the agent, run the `run.py` script from the `coding_agent_python` directory:

```bash
python run.py
```

This will start an interactive chat session with the AI agent. Type your requests or instructions, and the agent will respond or use its tools as needed. Type `exit` to end the conversation.

Example interaction:
```
Chat with the agent. Type 'exit' to end the conversation.

👤 > List files in the current directory.
🤖 Attempting to execute tool: list_files with input: {'path': '.'}
⚙️ Tool list_files result: {'status': 'success', 'files': ['./venv/', './run.py', './agent/', ...]}
🤖 Okay, I've listed the files in the current directory. Some of them include: ./venv/, ./run.py, ./agent/ ... What next?

👤 > Can you read the first 2 lines of run.py?
...
```

## Running Tests

The project uses `pytest` for tool tests and `unittest` for some specific cases (like `run_shell_command` tests that use mocking).

To run all tests:

1.  Ensure you have the development dependencies installed (pytest is in `requirements.txt`).
2.  Navigate to the `coding_agent_python` directory.
3.  Run pytest:
    ```bash
    pytest
    ```
    Or, to run unittest-style tests directly (though pytest should discover them):
    ```bash
    python -m unittest discover -s tests/tools -p "test_*.py"
    ```
    `pytest` is generally the recommended way as it will discover all tests.

## Project Structure

*   `agent/`: Core agent logic and tool definitions.
    *   `agent.py`: Main agent class, handles LLM interaction and tool dispatching.
    *   `tools/`: Individual tool implementations (`edit_file.py`, `list_files.py`, etc.).
*   `run.py`: Main executable script to start the agent.
*   `tests/`: Unit and integration tests for the tools.
*   `requirements.txt`: Python package dependencies.
*   `.env.example`: Example environment file (copy to `.env` and fill in).
*   `README.md`: This file.
*   `LICENSE`: Project license.
*   `Dockerfile`: For building a Docker image of the agent (see below).
*   `run_in_docker.sh`: Script to build and run the agent in Docker.

## Docker

This project can be run in Docker, which eliminates the need to set up a Python environment on your local machine.

### Running with Docker Locally

The easiest way to run the agent with Docker locally is to use the provided `run_in_docker.sh` script:

```bash
chmod +x run_in_docker.sh
./run_in_docker.sh
```

This script will:
1. Build the Docker image locally
2. Mount your current directory to the container's `/workspace` directory
3. Load environment variables from a `.env` file (make sure to create one with your ANTHROPIC_API_KEY)
4. Start the agent in interactive mode

### Using the Docker Hub Image

You can also pull and run the pre-built Docker image directly from Docker Hub:

```bash
# Pull the latest image
docker pull [your-dockerhub-username]/coding-agent-python:latest

# Run the container
docker run -it --rm \
  -v "$(pwd):/workspace" \
  --env ANTHROPIC_API_KEY="your_api_key_here" \
  [your-dockerhub-username]/coding-agent-python:latest
```

### Building and Pushing to Docker Hub

If you want to build and push your own version to Docker Hub:

```bash
# Login to Docker Hub
docker login

# Build the image
docker build -t [your-dockerhub-username]/coding-agent-python:latest .

# Push to Docker Hub
docker push [your-dockerhub-username]/coding-agent-python:latest
```

Replace `[your-dockerhub-username]` with your actual Docker Hub username.