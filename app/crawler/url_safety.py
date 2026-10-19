import ipaddress
import socket
from urllib.parse import urlparse

class UnsafeURLError(ValueError):
    """Raised When a URL points somewhere the crawler must not go."""

def _check_ip(ip) -> None:
    if getattr(ip, "ipv4_mapped", None):
        ip = ip.ipv4_mapped
    if not ip.is_global or ip.is_multicast:
        raise UnsafeURLError(f"Blocked non-public address: {ip}")

def validate_url(url: str) -> str:
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise UnsafeURLError("Only http and https URLs are allowed")
    if not parsed.hostname:
        raise UnsafeURLError("URL has no hostname")
    if parsed.username or parsed.password:
        raise UnsafeURLError("URLs with credentials are not allowed")

    try:
        port = parsed.port
    except ValueError as exc:
        raise UnsafeURLError("Invalid port") from exc
    port = port or (443 if parsed.scheme == "https" else 80)

    try:
        infos = socket.getaddrinfo(parsed.hostname,port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise UnsafeURLError(f"Cannot resolve host: {parsed.hostname}") from exc

    for info in infos:
        _check_ip(ipaddress.ip_address(info[4][0]))
    return url