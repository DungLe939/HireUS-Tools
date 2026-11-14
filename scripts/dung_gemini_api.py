#!/usr/bin/env python3
"""Small local client for the Trạm Mây OpenAI-compatible gateway."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = {
    "GEMINI_BASE_URL": "",
    "GEMINI_MODEL": "ag/gemini-3.8-flash-low",
    "GEMINI_REASONING_EFFORT": "low",
    "GEMINI_TRANSPORT": "curl",
}


def load_settings(env_path=None):
    """Read literal dotenv values, then apply OS overrides; never execute dotenv."""
    values = dict(DEFAULTS)
    path = Path(env_path) if env_path is not None else ROOT / ".env"
    sources = [{}]
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line.startswith("export "):
                line = line[7:].strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            sources[0][key.strip()] = value
    sources.append(os.environ)
    for source in sources:
        for key in (*DEFAULTS, "GEMINI_API_KEY"):
            if key in source:
                values[key] = source[key]
            elif key.lower() in source:
                values[key] = source[key.lower()]
    return values


class GeminiProxyClient:
    def __init__(self, settings=None, timeout=180):
        self.settings = dict(load_settings() if settings is None else settings)
        self.timeout = float(timeout)
        if self.timeout <= 0:
            raise ValueError("Timeout phải lớn hơn 0.")
        key = self.settings.get("GEMINI_API_KEY", "")
        if not key or any(c in key for c in "\r\n"):
            raise ValueError("Thiếu platform key hợp lệ trong GEMINI_API_KEY.")
        url = urlsplit(self.settings.get("GEMINI_BASE_URL", ""))
        if (url.scheme != "https" or not url.hostname or url.username or url.password
                or url.query or url.fragment):
            raise ValueError("GEMINI_BASE_URL phải là HTTPS URL, không chứa credentials/query/fragment.")
        if self.settings.get("GEMINI_TRANSPORT", "curl") != "curl":
            raise ValueError("Client này hỗ trợ GEMINI_TRANSPORT=curl.")

    def _request(self, route, payload=None):
        quote = lambda value: json.dumps(str(value), ensure_ascii=False)
        config = ["silent", "show-error", "max-redirs = 0",
                  "max-time = " + quote(self.timeout),
                  "url = " + quote(self.settings["GEMINI_BASE_URL"].rstrip("/") + route),
                  "header = " + quote("Authorization: Bearer " + self.settings["GEMINI_API_KEY"]),
                  'write-out = "\\n%{http_code}"']
        if payload is not None:
            config += ['request = "POST"', 'header = "Content-Type: application/json"',
                       "data-binary = " + quote(json.dumps(payload, ensure_ascii=False))]
        try:
            result = subprocess.run(
                ["curl", "--disable", "--config", "-"], input="\n".join(config) + "\n",
                text=True, capture_output=True, timeout=self.timeout + 5,
            )
        except FileNotFoundError:
            raise RuntimeError("Không tìm thấy curl trong PATH.") from None
        except subprocess.TimeoutExpired:
            raise RuntimeError("Hết thời gian gọi gateway; chưa tự retry.") from None
        if result.returncode:
            hint = {6: "Không phân giải được hostname/DNS.", 28: "Request timeout."}
            raise RuntimeError(hint.get(result.returncode, f"curl thất bại (exit {result.returncode})."))
        body, separator, status = result.stdout.rpartition("\n")
        if not separator or not status.isdigit():
            raise RuntimeError("Phản hồi thiếu HTTP status.")
        if not 200 <= int(status) < 300:
            hints = {401: "Kiểm tra platform key.", 403: "Kiểm tra quyền hoặc WAF.",
                     429: "Dừng gửi thêm request; kiểm tra quota/rate limit."}
            raise RuntimeError(f"HTTP {status}. " + hints.get(int(status), "Không tự retry hoặc theo redirect."))
        try:
            response = json.loads(body)
        except json.JSONDecodeError:
            raise RuntimeError("Gateway trả nội dung không phải JSON hợp lệ.") from None
        if not isinstance(response, dict) or "error" in response:
            raise RuntimeError("Gateway trả response lỗi hoặc sai cấu trúc.")
        return response

    def list_models(self):
        return self._request("/models")

    def chat(self, messages, max_tokens=1024):
        payload = {"model": self.settings["GEMINI_MODEL"], "messages": messages,
                   "max_tokens": max_tokens}
        effort = self.settings.get("GEMINI_REASONING_EFFORT")
        if effort:
            payload["reasoning_effort"] = effort
        return self._request("/chat/completions", payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list-models", action="store_true")
    parser.add_argument("--model")
    parser.add_argument("--prompt")
    args = parser.parse_args()
    if not args.list_models and not args.prompt:
        parser.error("Chọn --list-models hoặc --prompt.")
    try:
        settings = load_settings()
        if args.model:
            settings["GEMINI_MODEL"] = args.model
        client = GeminiProxyClient(settings)
        if args.list_models:
            response = client.list_models()
            print("\n".join(m["id"] for m in response["data"]))
        else:
            response = client.chat([{"role": "user", "content": args.prompt}], max_tokens=128)
            print(response["choices"][0]["message"]["content"])
    except (ValueError, RuntimeError, KeyError, TypeError) as error:
        parser.exit(1, f"Lỗi: {error}\n")


if __name__ == "__main__":
    main()
