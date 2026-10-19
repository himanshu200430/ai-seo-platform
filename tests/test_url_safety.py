import pytest

from app.crawler.url_safety import UnsafeURLError, validate_url


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost/",
        "http://127.0.0.1/",
        "http://10.0.0.5/",
        "http://192.168.1.1/",
        "http://172.16.0.1/",
        "http://169.254.169.254/latest/meta-data/",
        "http://[::1]/",
        "http://0.0.0.0/",
        "file:///etc/passwd",
        "ftp://example.com/",
        "http://user:pass@8.8.8.8/",
        "http:///nohost",
    ],
)
def test_unsafe_urls_blocked(url):
    with pytest.raises(UnsafeURLError):
        validate_url(url)


def test_public_ip_allowed():
    assert validate_url("http://8.8.8.8/") == "http://8.8.8.8/"