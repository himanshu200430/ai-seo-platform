import logging
import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["date", "page", "clicks", "impressions", "position"]

# CSV mein jo bhi naam ho, hum use apne standard naam pe le aate hain

COLUMN_ALIASES = {
    "date": "date", "day": "date",
    "page": "page", "pages": "page", "top pages": "page",
    "landing page": "page", "page url": "page", "url": "page",
    "clicks": "clicks",
    "impressions": "impressions",
    "position": "position", "average position": "position",
    "avg position": "position",
}

def load_gsc_csv(source) -> pd.DataFrame:
    df = pd.read_csv(source)
    df.columns = [str(c).strip().lower() for c in df.columns]
    df = df.rename(columns={c: COLUMN_ALIASES[c] for c in df.columns if c in COLUMN_ALIASES})

    if df.columns.duplicated().any():
        raise ValueError(f"CSV has columns that amp to the same field: {list(df.columns)}")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"CSV is missing required columns: {missing}. Found: {list(df.columns)}"
        )
    df = df[REQUIRED_COLUMNS].copy() # CTR waghera extra columns hat gaye
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["clicks", "impressions"]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", "", regex=False), errors="coerce"
        )
    df["position"] = pd.to_numeric(df["position"], errors="coerce")

    bad_rows = df.isna().any(axis=1)
    if bad_rows.any():
        logger.warning("Dropping %d unreadable rows", int(bad_rows.sum()))
        df = df[~bad_rows]
    if df.empty:
        raise ValueError("No valid rows left after cleaning the CSV")
    if(df["clicks"] > df["impressions"]).any():
        raise ValueError("Found rowws where clicks are greater than impressions")
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    return df.sort_values(["date","page"]).reset_index(drop=True)