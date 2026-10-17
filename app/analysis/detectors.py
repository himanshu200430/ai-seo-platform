import uuid
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from app.analysis.schemas import Issue

def _split_windows(df: pd.DataFrame, window_days: int):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    end = df["date"].max()
    cur_start = end - pd.Timedelta(days=window_days -1)
    prev_end = cur_start - pd.Timedelta(days=1)
    prev_start = prev_end - pd.Timedelta(days=window_days - 1)
    cur = df[(df["date"] >= cur_start) & (df["date"] <= end)]
    prev = df[(df["date"] >= prev_start) & (df["date"] <= prev_end)]
    label = (f"{cur_start.date()}..{end.date()} vs" f"{prev_start.date()}..{prev_end.date()}")
    return cur, prev, label

def detect_ctr_decline(
    gsc: pd.DataFrame,
    website: str,
    window_days: int = 28,
    min_impressions: int = 500,
    min_rel_drop: float = 0.25,
    min_z: float = 2.0,
) -> list[Issue]:
    cur, prev, label = _split_windows(gsc, window_days)
    agg = lambda d: d.groupby("page")[["clicks","impressions"]].sum()
    m = agg(prev).join(agg(cur), lsuffix="_prev", rsuffix="_cur", how="inner")
    m = m[(m["impressions_prev"] >= min_impressions) & (m["impressions_cur"] >= min_impressions)]
    issues: list[Issue] = []
    for page, r in m.iterrows():
        ctr_prev = r["clicks_prev"] / r["impressions_prev"]
        ctr_cur = r["clicks_cur"] / r["impressions_cur"]
        if ctr_prev == 0:
            continue
        rel_drop = (ctr_prev - ctr_cur) / ctr_prev
        if rel_drop < min_rel_drop:
            continue

        # two-proportion z-test: kya girawat sirf randomness ho sakti hai?
        pooled = (r["clicks_prev"] + r["clicks_cur"]) / (r["impressions_prev"] + r["impressions_cur"])
        se = np.sqrt(pooled * (1 - pooled) * (1/r["impressions_prev"] + 1/r["impressions_cur"]))
        z = (ctr_prev - ctr_cur) / se if se > 0 else 0.0
        if z < min_z:
            continue
        
        issues.append(Issue(
            issue_id = str(uuid.uuid4()),
            website=website,
            page_url=str(page),
            issue_type="ctr_decline",
            supporting_metrics={
                "ctr_previous": float(ctr_prev),
                "ctr_current": float(ctr_cur),
                "relative_drop": float(rel_drop),
                "impressions_previous": float(r["impressions_prev"]),
                "impressions_current": float(r["impressions_cur"]),
                "z_score": float(z),
            },
            comparison_period=label,
            severity="high" if rel_drop >= 0.5 else "medium",
            confidence="high" if z >= 3 else "medium",
            detected_at=datetime.now(timezone.utc),
            suggested_next_investigation=(
                "Check title/meta description changes, SERP feature changes, "
                "and average position for this page in the same period."
            ),
        ))
    return issues

