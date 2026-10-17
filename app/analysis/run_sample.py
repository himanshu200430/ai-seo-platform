import pandas as pd

from app.analysis.detectors import (
    detect_ctr_decline,
    detect_low_ctr_opportunity,
    detect_traffic_decline,
)
from app.analysis.sample_data import build_sample_data

if __name__ == "__main__":
    gsc, _ = build_sample_data()
    issues = (
        detect_ctr_decline(gsc, "example.com")
        + detect_traffic_decline(gsc, "example.com")
        + detect_low_ctr_opportunity(gsc, "example.com")
    )
    rows = [
        {"page": i.page_url, "type": i.issue_type,
         "severity": i.severity, "confidence": i.confidence}
        for i in issues
    ]
    print(pd.DataFrame(rows).sort_values("page").to_string(index=False))