from app.crawler.issues import crawl_to_issues


def test_crawl_to_issues(sample_crawl):
    issues = crawl_to_issues(sample_crawl, "example.com")
    found = {(i.issue_type, i.page_url) for i in issues}

    assert found == {
        ("missing_meta_description", "https://example.com/"),
        ("missing_h1", "https://example.com/b"),
        ("duplicate_title", "https://example.com/a"),
        ("duplicate_title", "https://example.com/b"),
        ("duplicate_meta_description", "https://example.com/a"),
        ("duplicate_meta_description", "https://example.com/b"),
        ("broken_internal_link", "https://example.com/gone"),
    }
    assert all(i.confidence == "high" for i in issues)