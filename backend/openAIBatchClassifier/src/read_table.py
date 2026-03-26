import os
import pandas as pd
from . import config


def _load_table(path: str):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(path)
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(path)
    raise ValueError(f"Unsupported input file extension: {ext}")


def _canonical_platform(value: str):
    raw = (value or "").strip().lower()
    if "android" in raw or "google" in raw:
        return "Android"
    if "ios" in raw or "apple" in raw:
        return "iOS"
    return ""


def _resolve_column(df: pd.DataFrame, preferred: str, candidates: list[str]):
    if preferred in df.columns:
        return preferred
    lowered = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]
    raise KeyError(
        f"Could not resolve required column. Tried: {', '.join(candidates)}"
    )


def read_app_table(input_path: str | None = None, ids_only: bool = True):
    """Load and normalize app metadata for scraping and merge steps.

    Supports both CSV and Excel inputs. For scraper outputs, `appId` and store labels
    are normalized into canonical `id` + `platform` columns.
    """
    path = input_path or config.DATA_FILE
    df = _load_table(path)

    id_col = _resolve_column(df, config.COL_ID, [config.COL_ID, "appId", "app_id"])
    platform_col = _resolve_column(
        df,
        config.COL_PLATFORM,
        [config.COL_PLATFORM, "store", "targetStore"],
    )

    if id_col != "id":
        df = df.rename(columns={id_col: "id"})
    if platform_col != "platform":
        df = df.rename(columns={platform_col: "platform"})

    df["id"] = df["id"].astype(str).str.strip()
    df["platform"] = df["platform"].astype(str).str.strip().map(_canonical_platform)
    df = df[(df["id"] != "") & (df["platform"].isin(["iOS", "Android"]))]

    if ids_only:
        df = df[["id", "platform"]].drop_duplicates(subset=["platform", "id"])
    return df
