#!/usr/bin/env python3

import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from agent.agent import Agent
except ModuleNotFoundError as e:
    print(f"Error: Could not import the Agent class: {e}")
    print("Ensure that the script is run from the 'coding_agent_python' directory, for example: python run.py")
    print("Or that 'coding_agent_python' directory is in your PYTHONPATH.")
    sys.exit(1)

def main():
    """
    Main function to initialize and run the agent.
    """
    try:
        agent_instance = Agent()
        agent_instance.run()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please ensure your ANTHROPIC_API_KEY is set in a .env file in the project root ('coding_agent_python/.env'),")
        print("or as an environment variable.")
    except Exception as e:
        print(f"An unexpected error occurred during agent execution: {e}")

if __name__ == "__main__":
    main() 