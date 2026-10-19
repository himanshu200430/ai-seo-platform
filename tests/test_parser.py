from app.crawler.parser import parse_page

HTML = """
<html><head>
<title> My Page </title>
<meta name="Description" content="A test page">
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="/main">
</head><body>
<h1>Hello</h1><h1>   </h1>
<a href="/about">About</a>
<a href="/about#team">About team</a>
<a href="https://other.com/x">Other</a>
<a href="mailto:a@b.com">Mail</a>
</body></html>
"""


def test_parse_page_extracts_basics():
    p = parse_page(HTML, "https://example.com/start")
    assert p.title == "My Page"
    assert p.meta_description == "A test page"
    assert p.robots_meta == "noindex, follow"
    assert p.canonical_url == "https://example.com/main"
    assert p.h1 == ["Hello"]
    assert p.internal_links == ["https://example.com/about"]
    assert p.external_links == ["https://other.com/x"]


def test_missing_fields_are_none():
    p = parse_page("<html><body>hi</body></html>", "https://example.com/")
    assert p.title is None
    assert p.meta_description is None
    assert p.canonical_url is None
    assert p.h1 == []