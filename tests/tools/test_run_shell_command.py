# Placeholder for tool tests: run_shell_command 

import os
import sys
import unittest
from unittest.mock import patch

# Ensure the agent tools can be imported
project_root_for_tests = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root_for_tests not in sys.path:
    sys.path.insert(0, project_root_for_tests)

from agent.tools import run_shell_command

class TestRunShellCommand(unittest.TestCase):

    @patch('builtins.input', return_value='y')
    def test_execute_command_when_approved(self, mock_input):
        command_to_run = "echo test_execution_approved"
        result = run_shell_command.execute(command=command_to_run)
        
        mock_input.assert_called_once()
        self.assertEqual(result.get("status"), "success")
        self.assertIn("test_execution_approved", result.get("stdout", ""))

    @patch('builtins.input', return_value='n')
    def test_reject_command_execution(self, mock_input):
        command_to_run = "echo test_execution_rejected"
        result = run_shell_command.execute(command=command_to_run)
        
        mock_input.assert_called_once()
        self.assertEqual(result.get("status"), "declined")
        self.assertEqual(result.get("message"), "User declined to execute the command.")

    @patch('builtins.input', return_value='y')
    def test_command_failure_returns_error_status(self, mock_input):
        command_to_run = "this_command_should_not_exist_anywhere_123xyz"
        result = run_shell_command.execute(command=command_to_run)
        
        mock_input.assert_called_once()
        self.assertEqual(result.get("status"), "error")
        self.assertIn("failed with return code", result.get("error", ""))
        self.assertTrue(len(result.get("stderr", "")) > 0 or len(result.get("error", "")) > 0)

    @patch('builtins.input', return_value='y')
    @patch('agent.tools.run_shell_command.subprocess.run')
    def test_subprocess_exception_returns_error(self, mock_subprocess_run, mock_input):
        mock_subprocess_run.side_effect = Exception("Subprocess boom!")
        command_to_run = "echo this_will_be_mocked"
        
        result = run_shell_command.execute(command=command_to_run)
        
        mock_input.assert_called_once()
        mock_subprocess_run.assert_called_once()
        self.assertEqual(result.get("status"), "error")
        self.assertEqual(result.get("error"), "Subprocess boom!")

if __name__ == '__main__':
    unittest.main() 