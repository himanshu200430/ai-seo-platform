from app.crawler.fetcher import fetch_page


def test_fetch_blocks_private_address_without_network():
    result = fetch_page("http://127.0.0.1/")
    assert result.html is None
    assert "Blocked" in result.error