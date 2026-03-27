import pandas as pd
import pytest

from backend.openAIBatchClassifier.src import read_table


def test_read_app_table_normalizes_csv_appid_and_store(tmp_path):
    csv_path = tmp_path / "apps.csv"
    pd.DataFrame(
        {
            "appId": [" com.foo.app ", "com.foo.app", "com.bar.app", "x"],
            "store": [
                "Apple App Store",
                "Apple App Store",
                "Google Play Store",
                "Windows",
            ],
            "title": ["A", "A", "B", "C"],
        }
    ).to_csv(csv_path, index=False)

    out = read_table.read_app_table(input_path=str(csv_path), ids_only=True)

    assert list(out.columns) == ["id", "platform"]
    assert set(map(tuple, out[["id", "platform"]].values.tolist())) == {
        ("com.foo.app", "iOS"),
        ("com.bar.app", "Android"),
    }


def test_read_app_table_missing_required_columns_raises(tmp_path):
    csv_path = tmp_path / "bad.csv"
    pd.DataFrame({"title": ["No id/platform"]}).to_csv(csv_path, index=False)

    with pytest.raises(KeyError):
        read_table.read_app_table(input_path=str(csv_path), ids_only=True)


def test_read_app_table_ids_only_false_keeps_other_columns(tmp_path):
    csv_path = tmp_path / "apps_full.csv"
    pd.DataFrame(
        {
            "id": ["a.pkg", "b.pkg"],
            "platform": ["Android", "iOS"],
            "title": ["A", "B"],
        }
    ).to_csv(csv_path, index=False)

    out = read_table.read_app_table(input_path=str(csv_path), ids_only=False)

    assert "title" in out.columns
    assert set(map(tuple, out[["id", "platform"]].values.tolist())) == {
        ("a.pkg", "Android"),
        ("b.pkg", "iOS"),
    }
