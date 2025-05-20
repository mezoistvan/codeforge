# Placeholder for tool tests: read_file 

import os
import tempfile
import shutil

# Ensure the agent tools can be imported
import sys
project_root_for_tests = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root_for_tests not in sys.path:
    sys.path.insert(0, project_root_for_tests)

from agent.tools import read_file

def test_read_existing_file():
    expected_content = "The cake is a lie!\n" 
    
    tmp_file = tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt", encoding="utf-8")
    file_path = tmp_file.name
    try:
        tmp_file.write(expected_content)
        tmp_file.close()

        result = read_file.execute(path=file_path)
        
        assert result.get("status") == "success"
        assert result.get("content") == expected_content
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def test_read_missing_file():
    missing_file_path = os.path.join(tempfile.gettempdir(), f"missing_file_for_read_test_{os.urandom(8).hex()}.txt")
    if os.path.exists(missing_file_path):
        os.remove(missing_file_path)

    result = read_file.execute(path=missing_file_path)
    
    assert result.get("status") == "error"
    assert f"No such file or directory: '{missing_file_path}'" == result.get("error")

def test_read_directory_returns_error():
    with tempfile.TemporaryDirectory() as tmp_dir_path:
        result = read_file.execute(path=tmp_dir_path)
        assert result.get("status") == "error"
        assert f"Path is a directory, not a file: '{tmp_dir_path}'" == result.get("error") 