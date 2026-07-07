#!/usr/bin/env python3
import os
import sys
import json
import unittest
from unittest.mock import MagicMock, patch
import subprocess

# Ensure repository root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components from server for unit testing
from mcp_server.omni_mcp_server import (
    state,
    generate_video,
    edit_video,
    get_last_video,
    clear_session,
    SessionState
)

class TestMCPServerLogic(unittest.TestCase):
    def setUp(self):
        self.old_key = os.environ.get("GEMINI_API_KEY")
        os.environ["GEMINI_API_KEY"] = "mock-key"
        # Clear state before each test
        state.clear()

    def tearDown(self):
        if self.old_key is None:
            os.environ.pop("GEMINI_API_KEY", None)
        else:
            os.environ["GEMINI_API_KEY"] = self.old_key
        state.clear()

    @patch('mcp_server.omni_mcp_server._get_client')
    @patch('mcp_server.omni_mcp_server._poll_and_download_video')
    def test_generate_video_success(self, mock_poll, mock_get_client):
        # Setup mocks
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_interaction = MagicMock()
        mock_interaction.id = "v1_test_interaction_123456"
        mock_interaction.output_text = "Generated output description"
        mock_client.interactions.create.return_value = mock_interaction
        
        mock_poll.return_value = True

        # Call generate_video tool logic
        result = generate_video(prompt="A test video description", aspect_ratio="16:9")

        # Verify calls and state
        mock_client.interactions.create.assert_called_once_with(
            model="gemini-omni-flash-preview",
            input="A test video description",
            background=False,
            store=True,
            stream=False,
            generation_config={"video_config": {"task": "text_to_video"}},
            response_format={"type": "video", "aspect_ratio": "16:9", "delivery": "uri"}
        )
        
        mock_poll.assert_called_once()
        self.assertEqual(state.last_interaction_id, "v1_test_interaction_123456")
        self.assertEqual(state.turn_count, 1)
        self.assertIn("Success", result)
        self.assertIn("v1_test_interaction_123456", result)

    @patch('mcp_server.omni_mcp_server._get_client')
    @patch('mcp_server.omni_mcp_server._poll_and_download_video')
    def test_edit_video_success(self, mock_poll, mock_get_client):
        # Pre-populate state to simulate an active session
        state.last_interaction_id = "v1_initial_id"
        state.turn_count = 1
        state.save()

        # Setup mocks
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_interaction = MagicMock()
        mock_interaction.id = "v1_edited_id"
        mock_interaction.output_text = "Edited output description"
        mock_client.interactions.create.return_value = mock_interaction
        
        mock_poll.return_value = True

        # Call edit_video tool logic
        result = edit_video(edit_prompt="Add a red hat.")

        # Verify calls and state
        mock_client.interactions.create.assert_called_once_with(
            model="gemini-omni-flash-preview",
            input="Edit this keeping everything else identical. Add a red hat.",
            previous_interaction_id="v1_initial_id",
            background=False,
            store=True,
            stream=False,
            generation_config={"video_config": {"task": "edit"}},
            response_format={"type": "video", "aspect_ratio": "16:9", "delivery": "uri"}
        )
        
        self.assertEqual(state.last_interaction_id, "v1_edited_id")
        self.assertEqual(state.turn_count, 2)
        self.assertIn("Success", result)
        self.assertIn("v1_edited_id", result)

    def test_edit_video_no_session(self):
        # Call edit without session and verify error
        result = edit_video(edit_prompt="Add a red hat.")
        self.assertIn("[ERROR] No active video session found", result)

    def test_get_last_video(self):
        # Check initial state
        self.assertIn("No active video session", get_last_video())

        # Populate state and check
        state.last_interaction_id = "v1_test"
        state.last_video_path = "/path/to/video.mp4"
        state.turn_count = 3
        
        result = get_last_video()
        self.assertIn("v1_test", result)
        self.assertIn("/path/to/video.mp4", result)
        self.assertIn("3", result)

    def test_clear_session(self):
        state.last_interaction_id = "v1_test"
        state.turn_count = 1
        state.save()
        
        clear_session()
        self.assertIsNone(state.last_interaction_id)
        self.assertEqual(state.turn_count, 0)


class TestMCPServerTransport(unittest.TestCase):
    """
    Spawns the MCP server as a subprocess and tests standard JSON-RPC 2.0 communication.
    """
    def setUp(self):
        self.server_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "mcp_server",
            "omni_mcp_server.py"
        )
        
    def test_mcp_handshake_and_tool_list(self):
        # Spawn the process with stdin and stdout pipes
        proc = subprocess.Popen(
            [sys.executable, self.server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            # 1. Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            proc.stdin.write(json.dumps(init_request) + "\n")
            proc.stdin.flush()

            # Read initialize response
            line = proc.stdout.readline()
            response = json.loads(line)
            
            self.assertEqual(response.get("jsonrpc"), "2.0")
            self.assertEqual(response.get("id"), 1)
            self.assertIn("result", response)
            self.assertIn("capabilities", response["result"])
            self.assertIn("tools", response["result"]["capabilities"])

            # 2. Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            proc.stdin.write(json.dumps(initialized_notification) + "\n")
            proc.stdin.flush()

            # 3. Send tools/list request
            list_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            proc.stdin.write(json.dumps(list_request) + "\n")
            proc.stdin.flush()

            # Read tools/list response
            line = proc.stdout.readline()
            response = json.loads(line)

            self.assertEqual(response.get("jsonrpc"), "2.0")
            self.assertEqual(response.get("id"), 2)
            self.assertIn("result", response)
            self.assertIn("tools", response["result"])
            
            # Verify details of exposed tools
            tools = {t["name"]: t for t in response["result"]["tools"]}
            self.assertIn("generate_video", tools)
            self.assertIn("edit_video", tools)
            self.assertIn("get_last_video", tools)
            self.assertIn("clear_session", tools)
            
            self.assertIn("prompt", tools["generate_video"]["inputSchema"]["required"])
            self.assertIn("edit_prompt", tools["edit_video"]["inputSchema"]["required"])

        finally:
            if proc.stdin:
                proc.stdin.close()
            if proc.stdout:
                proc.stdout.close()
            if proc.stderr:
                proc.stderr.close()
            proc.terminate()
            proc.wait()

if __name__ == "__main__":
    unittest.main()
