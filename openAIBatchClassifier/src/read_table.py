import pandas as pd
from . import config

def read_app_table():
    df = pd.read_excel(config.DATA_XLSX)
    df = df.rename(columns={config.COL_ID: "id", config.COL_PLATFORM: "platform"})
    df = df[["id", "platform"]].dropna()
    df["id"] = df["id"].astype(str).str.strip()
    df["platform"] = df["platform"].astype(str).str.strip()
    df = df[df["platform"].isin(["iOS", "Android"])]
    df = df.drop_duplicates(subset=["platform", "id"])
    return df
