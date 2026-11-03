import json, os, time
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

class ProviderError(RuntimeError): pass

class HTTPSProvider:
    """Small OpenAI-compatible adapter. Confirm your provider's current API contract before use."""
    def __init__(self, base_url=None, model=None, api_key=None, timeout=20, retries=2):
        self.base_url = base_url or os.getenv("AI_BASE_URL", "")
        self.model = model or os.getenv("AI_MODEL", "")
        self.api_key = api_key or os.getenv("AI_API_KEY", "")
        parsed = urlparse(self.base_url)
        if parsed.scheme != "https" or not parsed.hostname: raise ProviderError("AI_BASE_URL must be a trusted HTTPS URL")
        if not self.model or not self.api_key: raise ProviderError("AI_MODEL and AI_API_KEY must be configured")
        self.timeout, self.retries = timeout, retries

    def call_model(self, messages):
        payload = json.dumps({"model": self.model, "messages": messages, "temperature": 0}).encode()
        request = Request(self.base_url, data=payload, method="POST", headers={"Content-Type":"application/json", "Authorization":f"Bearer {self.api_key}"})
        for attempt in range(self.retries + 1):
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"]
            except HTTPError as exc:
                if exc.code not in (429, 500, 502, 503, 504) or attempt == self.retries: raise ProviderError(f"provider HTTP {exc.code}") from exc
            except (URLError, TimeoutError) as exc:
                if attempt == self.retries: raise ProviderError("provider connection failed") from exc
            except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc: raise ProviderError("provider returned an unexpected response") from exc
            time.sleep(0.25 * (2 ** attempt))

class FakeProvider:
    def __init__(self, replies): self.replies, self.calls = list(replies), 0
    def call_model(self, messages):
        self.calls += 1
        if not self.replies: raise ProviderError("no fake reply configured")
        reply = self.replies.pop(0)
        if isinstance(reply, Exception): raise reply
        return reply
