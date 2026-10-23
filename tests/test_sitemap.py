from app.crawler.safe_http import TextResult
from app.crawler.sitemap import load_sitemap_urls, parse_sitemap

URLSET = (
    "<?xml version='1.0'?><urlset>"
    "<url><loc>https://example.com/a</loc></url>"
    "<url><loc>https://example.com/b</loc></url></urlset>"
)
INDEX = (
    "<sitemapindex><sitemap><loc>https://example.com/s2.xml</loc></sitemap>"
    "</sitemapindex>"
)


def test_parse_urlset_and_index():
    assert parse_sitemap(URLSET) == (
        ["https://example.com/a", "https://example.com/b"],
        [],
    )
    assert parse_sitemap(INDEX) == ([], ["https://example.com/s2.xml"])


def test_load_follows_index_and_drops_other_hosts():
    files = {
        "https://example.com/sitemap.xml": INDEX,
        "https://example.com/s2.xml": (
            "<urlset><url><loc>https://example.com/x</loc></url>"
            "<url><loc>https://evil.com/y</loc></url></urlset>"
        ),
    }

    def fake(url):
        if url in files:
            return TextResult(status_code=200, text=files[url])
        return TextResult(status_code=404)

    assert load_sitemap_urls("https://example.com", fetch=fake) == ["https://example.com/x"]