import unittest
from unittest.mock import Mock, patch

import httpx

from backend.gitlab_mr import _create_practice_mr

PERSONA_RESULT = (
    "Here you go.\n\n```python\nclass CartItem:\n    pass\n```\n\n"
    "## Injected Errors / Deviations\n- total() ignores quantity"
)


def gitlab_handler(request: httpx.Request) -> httpx.Response:
    if request.url.path.endswith("/merge_requests"):
        return httpx.Response(201, json={"web_url": "https://gitlab.com/u/p/-/merge_requests/1"})
    if request.url.path.endswith("/commits"):
        return httpx.Response(201, json={})
    return httpx.Response(
        201, json={"id": 42, "web_url": "https://gitlab.com/u/p", "default_branch": "main"}
    )


class CreatePracticeMrTests(unittest.TestCase):
    def setUp(self) -> None:
        self.requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            self.requests.append(request)
            return gitlab_handler(request)

        real_client = httpx.Client
        client_patcher = patch(
            "backend.gitlab_mr.httpx.Client",
            lambda **kwargs: real_client(transport=httpx.MockTransport(handler), **kwargs),
        )
        client_patcher.start()
        self.addCleanup(client_patcher.stop)

    @patch("backend.gitlab_mr.save_practice_repo")
    @patch("backend.gitlab_mr.execute_task", return_value=PERSONA_RESULT)
    def test_pushes_persona_code_and_opens_mr(self, _execute: Mock, save: Mock) -> None:
        _create_practice_mr("token", 7)

        paths = [request.url.path for request in self.requests]
        self.assertEqual(
            paths,
            [
                "/api/v4/projects",
                "/api/v4/projects/42/repository/commits",
                "/api/v4/projects/42/merge_requests",
            ],
        )
        self.assertEqual(self.requests[0].headers["Authorization"], "Bearer token")

        commit = httpx.Response(200, content=self.requests[1].content).json()
        self.assertEqual(commit["branch"], "feature/cart")
        self.assertEqual(commit["actions"][0]["file_path"], "cart.py")
        self.assertEqual(commit["actions"][0]["content"], "class CartItem:\n    pass\n")

        merge_request = httpx.Response(200, content=self.requests[2].content).json()
        self.assertEqual(merge_request["source_branch"], "feature/cart")
        self.assertNotIn("Injected Errors", merge_request["description"])

        gitlab_id, practice_repo = save.call_args.args
        self.assertEqual(gitlab_id, 7)
        self.assertEqual(practice_repo["mr_url"], "https://gitlab.com/u/p/-/merge_requests/1")
        self.assertEqual(practice_repo["answer_key"], PERSONA_RESULT)

    @patch("backend.gitlab_mr.save_practice_repo")
    @patch("backend.gitlab_mr.execute_task", return_value="No code.\n## Injected Errors / Deviations\nNone.")
    def test_rejects_response_without_code(self, _execute: Mock, save: Mock) -> None:
        with self.assertRaisesRegex(ValueError, "code block"):
            _create_practice_mr("token", 7)

        self.assertEqual(self.requests, [])
        save.assert_not_called()


if __name__ == "__main__":
    unittest.main()
