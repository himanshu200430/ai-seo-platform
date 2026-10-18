import argparse

import pandas as pd

from app.analysis.csv_import import load_gsc_csv
from app.analysis.detectors import(
    detect_ctr_decline,
    detect_low_ctr_opportunity,
    detect_traffic_decline,
)
from app.db.init_db import init_db
from app.db.repository import save_issues
from app.db.session import SessionLocal
from app.logging_setup import setup_logging

def main() -> None:
    parser = argparse.ArgumentParser(description="Analyse a GSC CSV export")
    parser.add_argument("csv_path")
    parser.add_argument("--site", required=True, help="website name, e.g. example.com")
    parser.add_argument("--save", action="store_true", help="save issues to the database")
    args = parser.parse_args()

    setup_logging()
    gsc = load_gsc_csv(args.csv_path)
    issues = (
        detect_ctr_decline(gsc, args.site)
        + detect_traffic_decline(gsc, args.site)
        + detect_low_ctr_opportunity(gsc, args.site)
    )

    if not issues:
        print("No issues found")
        return

    rows = [
        {"page": i.page_url, "type": i.issue_type,
        "severity": i.severity, "confidence": i.confidence}

        for i in issues
    ]
    print(pd.DataFrame(rows).sort_values("page").to_string(index=False))

    if args.save:
        init_db()
        with SessionLocal() as session:
            saved = save_issues(session, issues)
            session.commit()
            print(f"Saved {saved} issues to  the database")

if __name__ == "__main__":
    main()