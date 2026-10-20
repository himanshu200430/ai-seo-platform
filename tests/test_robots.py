from app.crawler.robots import RobotsPolicy, parse_robots


def test_disallow_and_allow():
    policy = parse_robots("User-agent: *\nDisallow: /private\n")
    assert policy.can_fetch("https://example.com/public")
    assert not policy.can_fetch("https://example.com/private/page")


def test_rule_for_our_bot_specifically():
    policy = parse_robots(
        "User-agent: AISEOBot\nDisallow: /\n\nUser-agent: *\nAllow: /\n"
    )
    assert not policy.can_fetch("https://example.com/anything")


def test_crawl_delay():
    policy = parse_robots("User-agent: *\nCrawl-delay: 5\n")
    assert policy.crawl_delay() == 5.0


def test_allow_all_and_block_all_policies():
    assert RobotsPolicy(None, allow_all=True).can_fetch("https://example.com/x")
    assert not RobotsPolicy(None, allow_all=False).can_fetch("https://example.com/x")