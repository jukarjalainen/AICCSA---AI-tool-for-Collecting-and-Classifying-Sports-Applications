import pandas as pd
import pytest

# Import the module under test and its config
from openAIBatchClassifier.src import read_table, config

def test_read_app_table_happy_path(tmp_path, monkeypatch):
    # Build a tiny test Excel with extra columns, whitespace, duplicates, and a bad platform
    df = pd.DataFrame({
        "id": [" com.foo.app ", "com.foo.app", "com.bar.app", "123456", None],
        "Platform": ["iOS", "iOS", "Android", "iOS", "Android"],  # one None id row will drop via dropna
        "score": [4.5, 4.5, 4.2, 4.9, 3.1],                       # should be ignored
        "icon": ["a.png", "a.png", "b.png", "c.png", "d.png"]
    })

    # Also add a row with unsupported platform to ensure it gets filtered out
    df = pd.concat([df, pd.DataFrame({"id":["com.bad.platform"], "Platform":["Windows"], "score":[1], "icon":["x.png"]})], ignore_index=True)

    xlsx_path = tmp_path / "apps.xlsx"
    df.to_excel(xlsx_path, index=False)

    # Point the code to our temp Excel, not the real one
    monkeypatch.setattr(config, "DATA_XLSX", str(xlsx_path))

    out = read_table.read_app_table()

    # Expect only id + platform columns
    assert list(out.columns) == ["id", "platform"]

    # Whitespace trimmed, duplicates removed (same platform+id), only iOS/Android kept
    expected = set([
        ("com.foo.app", "iOS"),
        ("com.bar.app", "Android"),
        ("123456", "iOS"),  # numeric ids allowed (as strings)
    ])
    assert set(map(tuple, out[["id", "platform"]].values.tolist())) == expected

def test_read_app_table_missing_columns_raises(tmp_path, monkeypatch):
    # Build an Excel missing the 'Platform' column → should raise KeyError on rename/select
    bad = pd.DataFrame({"id": ["com.foo.app"], "score": [4.5]})
    xlsx_path = tmp_path / "apps_missing_cols.xlsx"
    bad.to_excel(xlsx_path, index=False)

    monkeypatch.setattr(config, "DATA_XLSX", str(xlsx_path))

    with pytest.raises(KeyError):
        _ = read_table.read_app_table()

def test_read_app_table_filters_platform_values(tmp_path, monkeypatch):
    # Ensure only "iOS" and "Android" are retained (case-sensitive per current implementation)
    df = pd.DataFrame({
        "id": ["a", "b", "c", "d"],
        "Platform": ["iOS", "Android", "ios", "ANDROID"],  # lower/upper variants should be dropped
    })
    xlsx_path = tmp_path / "apps_platform.xlsx"
    df.to_excel(xlsx_path, index=False)
    monkeypatch.setattr(config, "DATA_XLSX", str(xlsx_path))

    out = read_table.read_app_table()
    assert set(map(tuple, out[["id","platform"]].values.tolist())) == {("a","iOS"), ("b","Android")}
