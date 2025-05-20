import os

def get_tool_schema():
    return {
        "name": "edit_file",
        "description": "Make edits to a text file. Replaces 'old_str' with 'new_str' in the given file. 'old_str' and 'new_str' MUST be different from each other. If the file specified with path doesn't exist, it will be created.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file"
                },
                "old_str": {
                    "type": "string",
                    "description": "Text to search for - must match exactly and must only have one match exactly"
                },
                "new_str": {
                    "type": "string",
                    "description": "Text to replace old_str with"
                }
            },
            "required": ["path", "old_str", "new_str"]
        }
    }

def execute(path: str, old_str: str, new_str: str) -> dict:
    """
    Make edits to a text file.
    Replaces 'old_str' with 'new_str' in the given file.
    If the file specified with path doesn't exist, it will be created.
    Uses str.replace(old, new, 1) to replace only the first occurrence.
    """
    try:
        content = ""
        if os.path.exists(path):
            with open(path, 'r') as f:
                content = f.read()
        
        if old_str == "" and not content: # Creating a new file with content
            new_content = new_str
        elif old_str == "": # Prepending to existing file if old_str is empty
             new_content = new_str + content
        else:
            new_content = content.replace(old_str, new_str, 1)

        with open(path, 'w') as f:
            f.write(new_content)
        return {"status": "success", "path": path}
    except Exception as e:
        return {"status": "error", "error": str(e)} 