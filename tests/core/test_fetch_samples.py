import importlib.util
import io
from pathlib import Path


def load_module_from_scripts():
    """Load the scripts/fetch_samples.py module by path so tests can call its functions."""
    base = Path(__file__).resolve().parents[2]
    mod_path = base / "scripts" / "fetch_samples.py"
    spec = importlib.util.spec_from_file_location("fetch_samples", str(mod_path))
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert module is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore
    return module


def make_fake_resp(content: bytes, headers: dict[str, str] | None = None):
    class FakeResp(io.BytesIO):
        def __init__(self, data: bytes, headers: dict | None = None):
            super().__init__(data)
            self._headers = headers or {}

        def getheader(self, name: str, default: str | None = None):
            return self._headers.get(name, default)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            # Match the base IO API return (None)
            return None

    return FakeResp(content, headers)


def test_is_direct_download_returns_false_for_html(monkeypatch):
    fetch = load_module_from_scripts()

    def fake_urlopen(req, timeout=...):
        return make_fake_resp(b"<html>not a file</html>", {"Content-Type": "text/html"})

    monkeypatch.setattr(fetch.urllib.request, "urlopen", fake_urlopen)
    assert fetch.is_direct_download("http://example.com/page") is False


def test_is_direct_download_true_for_binary(monkeypatch):
    fetch = load_module_from_scripts()

    def fake_urlopen(req, timeout=...):
        return make_fake_resp(b"\x00\x01\x02", {"Content-Type": "application/octet-stream"})

    monkeypatch.setattr(fetch.urllib.request, "urlopen", fake_urlopen)
    assert fetch.is_direct_download("http://example.com/file.bin") is True


def test_download_url_writes_file_and_sha256(monkeypatch, tmp_path):
    fetch = load_module_from_scripts()

    data = b"hello-world"

    def fake_urlopen(req, timeout=...):
        # For both HEAD and GET we'll return the same fake stream; HEAD usage
        # in download_url checks Content-Length via getheader, so include it.
        headers = {"Content-Length": str(len(data)), "Content-Type": "application/octet-stream"}
        return make_fake_resp(data, headers)

    monkeypatch.setattr(fetch.urllib.request, "urlopen", fake_urlopen)

    dest = tmp_path / "out.bin"
    fetch.download_url("http://example.com/file.bin", dest, non_interactive=True)

    assert dest.exists()
    content = dest.read_bytes()
    assert content == data
    # quick sha256 sanity-check
    import hashlib

    assert hashlib.sha256(content).hexdigest() == hashlib.sha256(data).hexdigest()


def test_download_url_skips_when_user_declines(monkeypatch, tmp_path):
    fetch = load_module_from_scripts()

    data = b"x" * (fetch.DEFAULT_LARGE_THRESHOLD + 1024)

    def fake_head(req, timeout=...):
        class H:
            def getheader(self, name, default=None):
                if name == "Content-Length":
                    return str(len(data))
                return "application/octet-stream"

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        return H()

    monkeypatch.setattr(fetch.urllib.request, "urlopen", fake_head)
    monkeypatch.setattr("builtins.input", lambda prompt=None: "n")

    dest = tmp_path / "large.bin"
    # Should not raise, but should skip creating the file
    fetch.download_url("http://example.com/large.bin", dest, non_interactive=False)
    assert not dest.exists()
