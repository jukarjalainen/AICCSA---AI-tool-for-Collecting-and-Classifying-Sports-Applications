import pandas as pd
from . import config

def read_app_table():
    """Load and normalize the mobile app metadata table used for scraping.

    The workflow is:
    1. Read the Excel file referenced by `config.DATA_XLSX`.
    2. Rename the configured id/platform columns to canonical "id"/"platform" headers.
    3. Keep just the identifier and platform columns, dropping rows that are entirely missing.
    4. Strip whitespace, filter to supported platforms ("iOS", "Android"), and remove duplicates.
    """
    df = pd.read_excel(config.DATA_XLSX)
    df = df.rename(columns={config.COL_ID: "id", config.COL_PLATFORM: "platform"})
    df = df[["id", "platform"]].dropna()
    df["id"] = df["id"].astype(str).str.strip()
    df["platform"] = df["platform"].astype(str).str.strip()
    df = df[df["platform"].isin(["iOS", "Android"])]
    df = df.drop_duplicates(subset=["platform", "id"])
    return df
