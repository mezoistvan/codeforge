# Placeholder for tool tests: edit_file 

import os
import tempfile
import shutil

# Ensure the agent tools can be imported
import sys
project_root_for_tests = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root_for_tests not in sys.path:
    sys.path.insert(0, project_root_for_tests)

from agent.tools import edit_file # Adjusted import path

# Helper to create a temporary directory for tests if needed, or use NamedTemporaryFile for single files.
# For these tests, individual temp files are mostly sufficient.

def test_editing_an_existing_file():
    # Using NamedTemporaryFile which handles deletion by default if delete=True (default)
    # For this test, we need to write, close, let tool operate, then reopen and check.
    # So, delete=False and manual cleanup is better.
    tmp_file = tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt")
    file_path = tmp_file.name
    try:
        tmp_file.write("This is some content to edit")
        tmp_file.close() # Close it so the tool can open/write it
        
        result = edit_file.execute(path=file_path, old_str="content", new_str="text")
        assert result.get("status") == "success"
        
        with open(file_path, 'r') as f_check:
            content = f_check.read()
        assert content == "This is some text to edit"
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def test_creating_a_new_file_with_empty_old_str():
    # Get a temp file name, ensure it's deleted so the tool creates it
    tf_descriptor, file_path = tempfile.mkstemp(suffix=".txt")
    os.close(tf_descriptor) # Close the descriptor
    os.remove(file_path) # Ensure file does not exist
    
    assert not os.path.exists(file_path), f"File {file_path} should not exist before test"

    try:
        result = edit_file.execute(path=file_path, old_str="", new_str="Some fresh content")
        assert result.get("status") == "success"
        
        with open(file_path, 'r') as f_check:
            content = f_check.read()
        assert content == "Some fresh content"
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def test_editing_non_existent_file_creates_it_with_no_change_if_old_str_not_empty():
    tf_descriptor, file_path = tempfile.mkstemp(suffix=".txt")
    os.close(tf_descriptor)
    os.remove(file_path)
    
    assert not os.path.exists(file_path), f"File {file_path} should not exist before test"

    try:
        # If old_str is non-empty and file is new, content is "". 
        # "".replace("abc", "def", 1) is "". This matches Ruby `"".sub("abc", "def")`.
        result = edit_file.execute(path=file_path, old_str="should_not_be_found", new_str="new text")
        assert result.get("status") == "success"
        
        with open(file_path, 'r') as f_check:
            content = f_check.read()
        assert content == "" # old_str was not found in the (newly created) empty file
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def test_old_str_not_found_in_existing_file():
    tmp_file = tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt")
    file_path = tmp_file.name
    original_content = "This is some existing text."
    try:
        tmp_file.write(original_content)
        tmp_file.close()
        
        result = edit_file.execute(path=file_path, old_str="non_existent_string", new_str="replacement")
        assert result.get("status") == "success"
        
        with open(file_path, 'r') as f_check:
            content = f_check.read()
        assert content == original_content # Content should be unchanged
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def test_empty_old_str_prepends_to_existing_file():
    tmp_file = tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt")
    file_path = tmp_file.name
    original_content = "existing content."
    try:
        tmp_file.write(original_content)
        tmp_file.close()
        
        result = edit_file.execute(path=file_path, old_str="", new_str="prepended text and ")
        assert result.get("status") == "success"
        
        with open(file_path, 'r') as f_check:
            content = f_check.read()
        assert content == "prepended text and existing content."
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def test_tool_returns_error_on_exception():
    # e.g. permission error. How to simulate this robustly is tricky.
    # For now, let's assume a non-writable path (e.g. root dir if not admin, or a dummy path)
    # This test is platform dependent and might fail in certain environments.
    # A more robust way would be to mock os.path.exists or open to raise an error.
    # For simplicity, we'll try a path that is generally not writable. 
    # On Linux/macOS, trying to write to '/' as a file will fail.
    # On Windows, a path like "C:\Windows\System32\cantwrite.txt" might work.
    
    # Let's test the error wrapping in the tool, not the OS permissions themselves.
    # We can mock `open` within the tool's module to raise an exception.
    # However, for now, we rely on the general structure: if `open` or `write` fails, an error is returned.
    # The existing tests cover success cases. This is more about the error wrapping.
    
    # Instead of complex mocking, let's check against a path that should be a directory by default.
    # The tool itself does not prevent trying to write to a path that is a directory.
    # `open(directory_path, 'w')` would raise IsADirectoryError or similar.
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Attempting to use a directory path as a file path for writing
        # This will likely cause an IsADirectoryError when open(path, 'w') is called.
        result = edit_file.execute(path=tmp_dir, old_str="a", new_str="b")
        assert result.get("status") == "error"
        error_msg = result.get("error", "").lower()
        # Check for common phrases in "Is a directory" errors or permission errors across platforms
        assert "is a directory" in error_msg or "permission denied" in error_msg or "access is denied" in error_msg 