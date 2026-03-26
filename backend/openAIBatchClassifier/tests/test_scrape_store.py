import json
import pandas as pd

from backend.openAIBatchClassifier.src import scrape_store


def test_get_desc_android_uses_cache(monkeypatch):
    cache = {"Android::com.example.app": "cached description"}

    def _should_not_run(*args, **kwargs):
        raise AssertionError("google_play_scraper.app should not be called for cached app")

    monkeypatch.setattr(scrape_store, "gp_app", _should_not_run)
    desc = scrape_store.get_desc_android("com.example.app", cache)
    assert desc == "cached description"


def test_get_desc_ios_uses_track_id_and_bundle_lookup(monkeypatch):
    called_urls = []

    class DummyResponse:
        def __init__(self, url):
            self.url = url

        def raise_for_status(self):
            return None

        def json(self):
            return {"results": [{"description": f"desc for {self.url}"}]}

    def _fake_get(url, timeout):
        called_urls.append(url)
        return DummyResponse(url)

    monkeypatch.setattr(scrape_store.requests, "get", _fake_get)

    cache = {}
    d1 = scrape_store.get_desc_ios("12345678", cache)
    d2 = scrape_store.get_desc_ios("com.bundle.app", cache)

    assert "lookup?id=12345678" in called_urls[0]
    assert "lookup?bundleId=com.bundle.app" in called_urls[1]
    assert d1.startswith("desc for")
    assert d2.startswith("desc for")


def test_run_scrape_writes_descriptions_jsonl(tmp_path, monkeypatch):
    out_dir = tmp_path / "out"
    desc_file = out_dir / "descriptions.jsonl"
    cache_file = out_dir / "desc_cache.json"

    monkeypatch.setattr(scrape_store.config, "OUT_DIR", str(out_dir))
    monkeypatch.setattr(scrape_store.config, "DESCRIPTIONS_JSONL", str(desc_file))
    monkeypatch.setattr(scrape_store, "CACHE_PATH", str(cache_file))

    df = pd.DataFrame(
        [
            {"id": "com.android.app", "platform": "Android"},
            {"id": "12345678", "platform": "iOS"},
        ]
    )
    monkeypatch.setattr(
        scrape_store.read_table,
        "read_app_table",
        lambda input_path, ids_only: df,
    )

    monkeypatch.setattr(
        scrape_store,
        "get_desc_android",
        lambda app_id, cache: f"android:{app_id}",
    )
    monkeypatch.setattr(
        scrape_store,
        "get_desc_ios",
        lambda app_id, cache: f"ios:{app_id}",
    )

    scrape_store.run_scrape()

    lines = [
        json.loads(line)
        for line in desc_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(lines) == 2
    assert lines[0] == {
        "id": "com.android.app",
        "platform": "Android",
        "description": "android:com.android.app",
    }
    assert lines[1] == {
        "id": "12345678",
        "platform": "iOS",
        "description": "ios:12345678",
    }
