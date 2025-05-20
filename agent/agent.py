import os
import anthropic
import json
import time
import threading
import sys
from dotenv import load_dotenv

# Import tool modules
from .tools import read_file, list_files, edit_file, run_shell_command

class LoadingIndicator:
    """A simple loading indicator class that shows an animation while waiting."""
    def __init__(self, message="Thinking"):
        self.message = message
        self.running = False
        self.spinner_thread = None
        self.spinner_chars = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
        
    def start(self):
        """Start the loading animation in a separate thread."""
        if self.running:
            return
        self.running = True
        self.spinner_thread = threading.Thread(target=self._spin)
        self.spinner_thread.daemon = True
        self.spinner_thread.start()
        
    def stop(self):
        """Stop the loading animation."""
        self.running = False
        if self.spinner_thread:
            self.spinner_thread.join()
        # Clear the line
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()
        
    def _spin(self):
        """The spinner animation function."""
        idx = 0
        while self.running:
            sys.stdout.write(f"\r{self.spinner_chars[idx]} {self.message}... ")
            sys.stdout.flush()
            time.sleep(0.1)
            idx = (idx + 1) % len(self.spinner_chars)


class Agent:
    def __init__(self):
        load_dotenv() # Load environment variables from .env
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables. Please set it in your .env file or system environment.")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_name = os.getenv("ANTHROPIC_DEFAULT_MODEL", "claude-3-sonnet-20240229") 
        
        self.tools = {
            read_file.get_tool_schema()["name"]: {
                "schema": read_file.get_tool_schema(),
                "execute": read_file.execute
            },
            list_files.get_tool_schema()["name"]: {
                "schema": list_files.get_tool_schema(),
                "execute": list_files.execute
            },
            edit_file.get_tool_schema()["name"]: {
                "schema": edit_file.get_tool_schema(),
                "execute": edit_file.execute
            },
            run_shell_command.get_tool_schema()["name"]: {
                "schema": run_shell_command.get_tool_schema(),
                "execute": run_shell_command.execute
            }
        }
        self.conversation_history = []
        self.system_prompt = """
        You are a helpful AI assistant. You have access to a set of tools to interact with the user's file system and run commands.
        
        You are working with a codebase located in the root folder. All user input and requests will be related to making changes, analyzing, or working with this codebase.
        
        When a user asks for something that requires a tool, think step by step.
        First, decide which tool is appropriate. Then, determine the parameters for the tool. Finally, call the tool.
        If you need to ask clarifying questions before using a tool, do so.
        If a tool execution is successful, summarize the result for the user. If a tool execution fails (e.g. file not found, command error) or is declined by the user, inform the user of the outcome and ask how they would like to proceed.
        
        Always try to be helpful and complete the user's request. When a tool provides structured output (like JSON or a dictionary), present the key information from that output to the user in a readable way, rather than just showing the raw data structure, unless the user specifically asks for the raw data. If a command is declined by the user, simply state that and ask what to do next."""

    def _execute_tool(self, tool_name: str, tool_input: dict):
        if tool_name not in self.tools:
            return {"status": "error", "error": f"Tool '{tool_name}' not found."}
        
        tool_executor = self.tools[tool_name]["execute"]
        print("\n" + "─" * 80)
        print(f"🤖 EXECUTING TOOL: {tool_name}")
        
        # Only display the file path for relevant operations
        if 'path' in tool_input:
            print(f"📄 File: {tool_input['path']}")
        # For shell commands, show the command being run
        elif 'command' in tool_input:
            print(f"🔄 Command: {tool_input['command']}")
        print("─" * 80)
        
        # Start loading indicator for tool execution
        loading = LoadingIndicator(f"Executing {tool_name}")
        loading.start()
        
        try:
            # For shell commands, we need to handle the confirmation process
            if tool_name == "run_shell_command":
                # Create a monitor function that watches stdout to detect confirmation requests
                original_write = sys.stdout.write
                
                def write_monitor(text):
                    # When the confirmation prompt appears, pause the loading indicator
                    if "🔍 CONFIRMATION REQUIRED" in text:
                        loading.stop()
                    # When command execution starts after confirmation, restart the indicator
                    elif "⚙️ EXECUTING COMMAND..." in text:
                        loading.start()
                    return original_write(text)
                
                # Replace stdout.write with our monitored version
                sys.stdout.write = write_monitor
                try:
                    result = tool_executor(**tool_input)
                finally:
                    # Restore the original stdout.write
                    sys.stdout.write = original_write
            else:
                # For all other tools, normal execution
                result = tool_executor(**tool_input)
        finally:
            loading.stop() # Always stop the loading indicator
            print("\n" + "─" * 80)
            print(f"⚙️ TOOL RESULT: {tool_name}")
            
            # Format the result for better readability
            if isinstance(result, dict):
                if "status" in result:
                    status_emoji = "✅" if result["status"] == "success" else "❌"
                    print(f"{status_emoji} Status: {result['status']}")
                
                for key, value in result.items():
                    if key != "status":
                        # Skip printing file content for read_file tool
                        if key == "content" and tool_name == "read_file":
                            print(f"• {key}: [content available but not displayed]")
                        elif key in ["stdout", "stderr"] and value:
                            print(f"\n📄 {key.upper()}:")
                            print("```")
                            print(value.rstrip())
                            print("```")
                        elif value:
                            print(f"• {key}: {value}")
            else:
                print(result)
                
            print("─" * 80)
            return result

    def run(self):
        print("\n" + "═" * 80)
        print("🤖 AGENT INITIALIZED")
        print("Chat with the AI assistant. Type 'exit' to end the session.")
        print("═" * 80)

        while True: # Outer loop for user input
            print("\n" + "═" * 80)
            user_input = input("👤 YOUR INPUT > ")
            if user_input.lower() == "exit":
                print("🤖 Exiting agent.")
                break
            
            if not user_input.strip(): # Skip empty input
                continue

            self.conversation_history.append({"role": "user", "content": user_input})

            # Pre-calculate tool schemas once per user turn, as they don't change
            current_tool_schemas = []
            for _tool_name, tool_data in self.tools.items():
                schema_copy = tool_data["schema"].copy() # Make a copy to modify
                if "parameters" in schema_copy:
                    schema_copy["input_schema"] = schema_copy.pop("parameters")
                current_tool_schemas.append(schema_copy)

            try:
                # Inner loop to handle a sequence of assistant responses and tool uses for a single user query
                while True:
                    messages_to_send = [msg for msg in self.conversation_history if msg.get('content')]
                    if not messages_to_send:
                        print("\n🤖 Error: No messages to send to API. This should not happen after user input.")
                        break # Break inner loop, go to next user input

                    # Start loading indicator
                    loading = LoadingIndicator("Model thinking")
                    loading.start()
                    
                    try:
                        api_response_obj = self.client.messages.create(
                            model=self.model_name,
                            max_tokens=2048,
                            system=self.system_prompt,
                            messages=messages_to_send,
                            tools=current_tool_schemas, # Always provide tools
                            tool_choice={"type": "auto"}  # Always allow auto tool choice
                        )
                    finally:
                        # Stop loading indicator regardless of success or failure
                        loading.stop()

                    assistant_turn_content_blocks = [] # Content blocks for this turn of assistant (text and tool_use)
                    text_response_parts = []
                    tool_calls_to_execute_this_turn = []

                    if api_response_obj.content:
                        for block in api_response_obj.content:
                            # Store raw block for history, using model_dump() if it's a Pydantic model
                            if hasattr(block, 'model_dump'):
                                assistant_turn_content_blocks.append(block.model_dump())
                            else: # Fallback if it's not a Pydantic model (should not happen with current SDK)
                                assistant_turn_content_blocks.append(block) 
                            
                            if block.type == 'text':
                                text_response_parts.append(block.text)
                            elif block.type == 'tool_use':
                                tool_calls_to_execute_this_turn.append({
                                    "id": block.id,
                                    "name": block.name,
                                    "input": block.input
                                })
                    
                    if text_response_parts:
                        full_text_response = "".join(text_response_parts)
                        print("\n" + "═" * 80)
                        print("🤖 ASSISTANT RESPONSE:")
                        print("═" * 80)
                        print(f"{full_text_response}")
                        print("═" * 80, end="")
                    
                    if assistant_turn_content_blocks:
                        self.conversation_history.append({
                            "role": "assistant", 
                            "content": assistant_turn_content_blocks
                        })
                    else:
                        # Handle cases where the model might return no content blocks
                        # (e.g., if only stop_reason is 'max_tokens' or an error state not caught by APIError)
                        if api_response_obj.stop_reason not in ['tool_use', 'end_turn', 'stop_sequence']:
                             print(f"\n🤖 Assistant response ended unexpectedly or with no content. Reason: {api_response_obj.stop_reason}")
                        print() # Ensure newline if nothing else printed this iteration
                        break # Break inner loop, as there's no actionable content

                    if not tool_calls_to_execute_this_turn:
                        print() # Ensure newline if text was printed without one, and no tools follow.
                        break # No tools to call, assistant's turn for this user input is over. Break inner loop.

                    # We have tools to execute for this turn
                    tool_results_for_next_user_message = []
                    for tool_call in tool_calls_to_execute_this_turn:
                        tool_name = tool_call['name']
                        tool_input = tool_call['input']
                        tool_use_id = tool_call['id']
                        
                        tool_result_data = self._execute_tool(tool_name, tool_input)
                        
                        tool_results_for_next_user_message.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": json.dumps(tool_result_data)
                        })

                    if tool_results_for_next_user_message:
                        self.conversation_history.append({
                            "role": "user", 
                            "content": tool_results_for_next_user_message
                        })
                    else:
                        # This case should ideally not be reached if tool_calls_to_execute_this_turn was non-empty
                        print("\n🤖 Error: Tools were scheduled but no results were generated.")
                        break # Break inner loop to avoid potential infinite loop

                    # Implicitly continue inner loop: the history now contains tool results,
                    # and the next iteration will make an API call with this updated history.

            except anthropic.APIError as e:
                print("\n" + "─" * 80)
                print("❌ API ERROR")
                print(f"🔴 {e}")
                print("─" * 80)
            except Exception as e:
                print("\n" + "─" * 80)
                print("❌ UNEXPECTED ERROR")
                print(f"🔴 {e}")
                print("─" * 80)
            
            if len(self.conversation_history) > 30: # Keep last 30 message objects (user or assistant)
                # This simple slicing might be too aggressive if one turn has many blocks.
                # A more nuanced pruning might count "turns" (user + assistant sequence).
                # For now, this is a basic safeguard.
                self.conversation_history = self.conversation_history[-30:]