import sys

from app.crawler.fetcher import fetch_page
from app.crawler.parser import parse_page

if __name__ == "__main__":
    result = fetch_page(sys.argv[1])
    print("status:", result.status_code, "| final url:", result.final_url, "| error:", result.error)
    if result.html:
        print(parse_page(result.html, result.final_url).model_dump_json(indent=2))