import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.dung_gemini_api import DEFAULTS, GeminiProxyClient, load_settings


class GeminiClientTests(unittest.TestCase):
    def settings(self):
        return dict(DEFAULTS, GEMINI_API_KEY="test-secret", GEMINI_BASE_URL="https://gateway.example/v1")

    def test_settings_os_overrides_legacy_file_key(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ".env"
            p.write_text("gemini_api_key='old'\nGEMINI_MODEL=file-model\n")
            with patch.dict(os.environ, {"GEMINI_API_KEY": "new"}, clear=True):
                s = load_settings(p)
            self.assertEqual(s["GEMINI_API_KEY"], "new")
            self.assertEqual(s["GEMINI_MODEL"], "file-model")

    @patch("scripts.dung_gemini_api.subprocess.run")
    def test_secret_stdin_and_image_payload(self, run):
        run.return_value = subprocess.CompletedProcess([], 0, '{"model":"alias"}\n200', '')
        messages = [{"role": "user", "content": [{"type": "image_url", "image_url": {"url": "data:image/png;base64,AA=="}}]}]
        result = GeminiProxyClient(self.settings()).chat(messages)
        argv = run.call_args.args[0]
        config = run.call_args.kwargs["input"]
        self.assertNotIn("test-secret", str(argv))
        self.assertEqual(argv, ["curl", "--disable", "--config", "-"])
        self.assertIn("Authorization: Bearer test-secret", config)
        data = next(l for l in config.splitlines() if l.startswith("data-binary = "))
        payload = json.loads(json.loads(data.split(" = ", 1)[1]))
        self.assertEqual(payload["messages"], messages)
        self.assertEqual(payload["reasoning_effort"], "low")
        self.assertEqual(result["model"], "alias")

    @patch("scripts.dung_gemini_api.subprocess.run")
    def test_http_failures_do_not_leak_response_or_retry(self, run):
        for status in (302, 401, 403, 429, 500):
            run.reset_mock()
            run.return_value = subprocess.CompletedProcess([], 0, 'test-secret\n'+str(status), '')
            with self.assertRaises(RuntimeError) as error:
                GeminiProxyClient(self.settings()).list_models()
            self.assertNotIn("test-secret", str(error.exception))
            run.assert_called_once()

    @patch("scripts.dung_gemini_api.subprocess.run")
    def test_transport_error_does_not_leak_stderr(self, run):
        run.return_value = subprocess.CompletedProcess([], 6, '', 'test-secret')
        with self.assertRaisesRegex(RuntimeError, 'DNS') as error:
            GeminiProxyClient(self.settings()).list_models()
        self.assertNotIn("test-secret", str(error.exception))

    def test_unsafe_auth_or_url_is_rejected(self):
        for extra in ({"GEMINI_API_KEY": "bad\nheader"}, {"GEMINI_BASE_URL": ""}, {"GEMINI_BASE_URL": "http://example.com"}, {"GEMINI_BASE_URL": "https://user:key@example.com"}):
            s = self.settings(); s.update(extra)
            with self.assertRaises(ValueError):
                GeminiProxyClient(s)


if __name__ == "__main__":
    unittest.main()
