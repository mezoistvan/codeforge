import os

def get_tool_schema():
    return {
        "name": "read_file",
        "description": "Read the contents of a given file path. Use this when you want to see what's inside a file. Do not use this with directory names.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The relative or absolute path of a file."
                }
            },
            "required": ["path"]
        }
    }

def execute(path: str) -> dict:
    """
    Read the contents of a given file path.
    Returns the file content as a string or an error message.
    """
    try:
        if not os.path.exists(path):
            return {"status": "error", "error": f"No such file or directory: '{path}'"} 
        
        if os.path.isdir(path):
            return {"status": "error", "error": f"Path is a directory, not a file: '{path}'"}

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "error": str(e)} 