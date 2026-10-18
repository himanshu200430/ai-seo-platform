from app.analysis.detectors import detect_ctr_decline
from app.analysis.sample_data import build_sample_data
from app.db.init_db import init_db
from app.db.repository import list_issues, save_issues
from app.db.session import SessionLocal

def test_save_and_read_issues():
    init_db()
    gsc, _ = build_sample_data()
    issues = detect_ctr_decline(gsc, website="test-site.example")
    assert issues

    with SessionLocal() as session:
        try:
            assert save_issues(session, issues) == len(issues)
            saved = list_issues(session, "test-site.example")
            assert {s.page_url for s in saved} == {i.page_url for i in issues}
        finally:
            session.rollback()