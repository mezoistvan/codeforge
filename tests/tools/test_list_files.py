# Placeholder for tool tests: list_files 

import os
import shutil
import tempfile

# Ensure the agent tools can be imported
import sys
project_root_for_tests = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root_for_tests not in sys.path:
    sys.path.insert(0, project_root_for_tests)

from agent.tools import list_files

def test_list_files_in_existing_directory():
    with tempfile.TemporaryDirectory() as tmp_root_dir:
        fixtures_path = os.path.join(tmp_root_dir, "test_fixtures")
        os.makedirs(fixtures_path)
        
        with open(os.path.join(fixtures_path, "readme.txt"), "w") as f:
            f.write("dummy content")
            
        os.makedirs(os.path.join(fixtures_path, "subfolder"))
        
        with open(os.path.join(fixtures_path, "subfolder", "another.txt"), "w") as f:
            f.write("sub content")

        expected_readme = os.path.join(fixtures_path, "readme.txt")
        expected_subfolder = os.path.join(fixtures_path, "subfolder") + os.sep

        result = list_files.execute(path=fixtures_path)
        
        assert result.get("status") == "success"
        actual_files = result.get("files", [])
        actual_files.sort()
        
        expected_files_sorted = sorted([expected_readme, expected_subfolder])
        assert actual_files == expected_files_sorted

def test_list_files_in_current_directory_if_path_empty_or_default():
    with tempfile.TemporaryDirectory() as tmp_cwd:
        original_cwd = os.getcwd()
        os.chdir(tmp_cwd)

        try:
            with open("file1.txt", "w") as f: f.write("1")
            os.makedirs("dir1")
            with open(os.path.join("dir1", "file2.txt"), "w") as f: f.write("2")

            # Items relative to tmp_cwd, tool also returns them relative to CWD (which is tmp_cwd)
            expected_items = sorted(["./dir1" + os.sep, "./file1.txt"])

            result_default = list_files.execute() 
            assert result_default.get("status") == "success"
            assert sorted(result_default.get("files", [])) == expected_items
            
            result_empty_path = list_files.execute(path="")
            assert result_empty_path.get("status") == "success"
            assert sorted(result_empty_path.get("files", [])) == expected_items
        finally:
            os.chdir(original_cwd)

def test_list_files_non_existent_path():
    # Use a highly unlikely path name within a standard temp directory
    non_existent_path = os.path.join(tempfile.gettempdir(), f"non_existent_dir_for_list_files_test_{os.urandom(8).hex()}")
    if os.path.exists(non_existent_path):
        if os.path.isdir(non_existent_path):
            shutil.rmtree(non_existent_path)
        else:
            os.remove(non_existent_path) # Should not be a file, but handle just in case

    result = list_files.execute(path=non_existent_path)
    assert result.get("status") == "success" 
    assert result.get("files", []) == [] 