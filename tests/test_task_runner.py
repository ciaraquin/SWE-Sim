import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import httpx

from backend.task_runner import execute_task


class ExecuteTaskTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)
        self.persona_file = self.directory / "persona.md"
        self.persona_file.write_text("Respond as a concise engineer.", encoding="utf-8")
        self.output_file = self.directory / "result.md"
        self.load_dotenv_patcher = patch("backend.task_runner.load_dotenv")
        self.load_dotenv_patcher.start()

    def tearDown(self) -> None:
        self.load_dotenv_patcher.stop()
        self.temporary_directory.cleanup()

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True)
    @patch("backend.task_runner.httpx.post")
    def test_sends_task_and_persona_and_saves_response(self, post: Mock) -> None:
        response = httpx.Response(
            200,
            json={
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_text",
                                "text": "Task complete.\n\n## Injected Errors / Deviations\nNone.",
                            }
                        ],
                    }
                ]
            },
            request=httpx.Request("POST", "https://api.openai.com/v1/responses"),
        )
        post.return_value = response

        result = execute_task("Write a summary.", self.persona_file, self.output_file)

        expected_result = "Task complete.\n\n## Injected Errors / Deviations\nNone."
        self.assertEqual(result, expected_result)
        self.assertEqual(self.output_file.read_text(encoding="utf-8"), expected_result)
        post.assert_called_once()
        request = post.call_args
        instructions = request.kwargs["json"]["instructions"]
        self.assertTrue(instructions.startswith("Respond as a concise engineer."))
        self.assertIn("## Injected Errors / Deviations", instructions)
        self.assertIn("persona-driven defects; do not fix them", instructions)
        self.assertEqual(request.kwargs["json"]["input"], "Write a summary.")
        self.assertEqual(request.kwargs["headers"]["Authorization"], "Bearer test-key")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True)
    @patch("backend.task_runner.httpx.post")
    def test_rejects_response_without_error_report(self, post: Mock) -> None:
        post.return_value = httpx.Response(
            200,
            json={
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": "Task complete."}],
                    }
                ]
            },
            request=httpx.Request("POST", "https://api.openai.com/v1/responses"),
        )

        with self.assertRaisesRegex(ValueError, "Injected Errors / Deviations"):
            execute_task("Write a summary.", self.persona_file, self.output_file)

        self.assertFalse(self.output_file.exists())

    @patch.dict(os.environ, {}, clear=True)
    def test_requires_api_key(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "OPENAI_API_KEY"):
            execute_task("Do work.", self.persona_file, self.output_file)

    def test_rejects_blank_task_description(self) -> None:
        with self.assertRaisesRegex(ValueError, "task_description"):
            execute_task("  ", self.persona_file, self.output_file)

    def test_rejects_blank_persona_file(self) -> None:
        self.persona_file.write_text("  ", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "persona file"):
            execute_task("Do work.", self.persona_file, self.output_file)


if __name__ == "__main__":
    unittest.main()
