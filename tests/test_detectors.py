from app.analysis.detectors import (detect_ctr_decline, detect_low_ctr_opportunity, detect_traffic_decline,)
from app.analysis.sample_data import build_sample_data

def test_ctr_decline_flags_blog_page_only():
    gsc, _ = build_sample_data()
    issues = detect_ctr_decline(gsc, website="example.com")
    pages = {i.page_url for i in issues}

    assert "/blog/seo-basics" in pages
    assert "/" not in pages
    assert "/pricing" not in pages 
    assert all(i.issue_type == "ctr_decline" for i in issues)

def test_traffic_decline_flags_pricing_not_home():
    gsc, _ = build_sample_data()
    pages = {i.page_url for i in detect_traffic_decline(gsc, website="example.com")}
    assert "/pricing" in pages
    assert "/" not in pages

def test_low_ctr_opportunity_flags_shoes_only():
    gsc, _ = build_sample_data()
    pages = {i.page_url for i in detect_low_ctr_opportunity(gsc, website="example.com")}
    assert pages == {"/products/shoes"}