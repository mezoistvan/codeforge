import subprocess

def get_tool_schema():
    return {
        "name": "run_shell_command",
        "description": "Execute a shell command. IMPORTANT: This tool will ask for user confirmation before running any command.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to execute."
                }
            },
            "required": ["command"]
        }
    }

def execute(command: str) -> dict:
    """
    Execute a shell command after user confirmation.
    Returns the standard output of the command or an error message.
    """
    try:
        # Signal that we're about to ask for confirmation - this will be used by the agent to stop the loading indicator
        print("\n\033[1m🔍 CONFIRMATION REQUIRED\033[0m")
        print(f"AI proposes to execute the following shell command: '{command}'")
        print("Do you want to execute this command? (y/n): ", end='', flush=True)
        
        response = input().strip().lower()

        if response != 'y':
            return {"status": "declined", "message": "User declined to execute the command."}

        # After confirmation, print a message indicating execution has started
        print("\n\033[1m⚙️ EXECUTING COMMAND...\033[0m")
        
        process = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

        if process.returncode == 0:
            return {"status": "success", "stdout": process.stdout, "stderr": process.stderr}
        else:
            error_message = f"Command '{command}' failed with return code {process.returncode}."
            return {"status": "error", "error": error_message, "stdout": process.stdout, "stderr": process.stderr}

    except Exception as e:
        return {"status": "error", "error": str(e)} 