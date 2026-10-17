from pathlib import Path

import numpy as np
import pandas as pd

OUT_DIR = Path("data/sample")

PAGES = {
    "/": {"imp": 900, "ctr": 0.060, "pos": 4.2},
    "/blog/seo-basics": {"imp": 700, "ctr": 0.050, "pos": 6.5},  # CTR girega
    "/pricing": {"imp": 400, "ctr": 0.045, "pos": 7.0},  # traffic girega
    "/products/shoes": {"imp": 1500, "ctr": 0.008, "pos": 9.5},  # hamesha low CTR
    "/about": {"imp": 120, "ctr": 0.030, "pos": 11.0},
    "/contact": {"imp": 60, "ctr": 0.040, "pos": 8.0},
}

def build_sample_data(seed: int = 42):
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end="2026-10-15", periods=56, freq="D")
    cutoff = dates[28]

    gsc_rows, ga4_rows = [], []
    for d in dates:
        recent = d >= cutoff
        day = d.strftime("%Y-%m-%d")
        for page, cfg in PAGES.items():
            imp_mean, ctr = cfg["imp"], cfg["ctr"]
            if page == "/blog/seo-basics" and recent:
                ctr *= 0.5
            if page == "/pricing" and recent:
                imp_mean *= 0.6

            impressions = int(rng.poisson(imp_mean))
            clicks = int(rng.binomial(impressions,ctr))
            position = round(float(rng.normal(cfg["pos"], 0.3)), 1)
            gsc_rows.append(
                {"date": day, "page": page, "clicks": clicks, "impressions": impressions, "position":position}
            )

            sessions = int(round(clicks * rng.uniform(0.9,1.0)))
            engaged = int(rng.binomial(sessions, 0.6))
            conversions = int(rng.binomial(engaged, 0.05))
            ga4_rows.append(
                {
                    "date": day, "landing_page": page, "organic_sessions": sessions,
                    "engaged_sessions": engaged, "conversions": conversions
                }
            )
    return pd.DataFrame(gsc_rows), pd.DataFrame(ga4_rows)

if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gsc, ga4 = build_sample_data()
    gsc.to_csv(OUT_DIR / "gsc_page_daily.csv", index=False)
    ga4.to_csv(OUT_DIR / "ga4_landing_pages.csv", index=False)
    print(f"Saved {len(gsc)} GSC rows and {len(ga4)} GA4 rows to {OUT_DIR}")

