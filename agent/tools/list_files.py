import os
import glob

def get_tool_schema():
    return {
        "name": "list_files",
        "description": "List files and directories at a given path. If no path is provided, lists files in the current working directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Optional relative or absolute path to list files from. Defaults to current working directory if not provided or empty."
                }
            },
            "required": [] # Path is optional
        }
    }

def execute(path: str = ".") -> dict:
    """
    List files and directories at a given path.
    If no path is provided or path is empty, lists files in the current working directory.
    Appends a '/' to directory names.
    """
    try:
        if not path: # Handle empty string path as current directory
            path = "."

        items = glob.glob(os.path.join(path, "*"))
        
        result_list = []
        for item_path in items:
            if os.path.isdir(item_path):
                result_list.append(item_path + os.sep) # Use os.sep for platform independence
            else:
                result_list.append(item_path)
        
        return {"status": "success", "files": sorted(result_list)} # Sort for consistent output
    except Exception as e:
        return {"status": "error", "error": str(e)} 