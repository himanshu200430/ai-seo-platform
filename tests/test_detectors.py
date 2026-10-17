from app.analysis.detectors import detect_ctr_decline
from app.analysis.sample_data import build_sample_data

def test_ctr_decline_flags_blog_page_only():
    gsc, _ = build_sample_data()
    issues = detect_ctr_decline(gsc, website="example.com")
    pages = {i.page_url for i in issues}

    assert "/blog/seo-basics" in pages
    assert "/" not in pages
    assert "/pricing" not in pages 
    assert all(i.issue_type == "ctr_decline" for i in issues)