from unittest.mock import MagicMock

from extract_emails.browsers import PageSourceGetter
from extract_emails.link_filters import DefaultLinkFilter
from extract_emails.workers import DefaultWorker


def make_browser(page_source: str = "") -> PageSourceGetter:
    browser = MagicMock(spec=PageSourceGetter)
    browser.get_page_source.return_value = page_source
    return browser


def test_default_depth():
    worker = DefaultWorker(
        website_url="https://example.com",
        browser=make_browser(),
    )
    assert worker.depth == 5


def test_default_max_links_from_page():
    worker = DefaultWorker(
        website_url="https://example.com",
        browser=make_browser(),
    )
    assert worker.max_links_from_page == 5


def test_custom_depth():
    worker = DefaultWorker(
        website_url="https://example.com",
        browser=make_browser(),
        depth=5,
    )
    assert worker.depth == 5


def test_depth_limits_crawl():
    """Worker should stop crawling after the given depth."""
    # Page source contains a link back to itself to generate infinite depth
    page_source = '<a href="https://example.com/page">link</a>'
    browser = make_browser(page_source)
    link_filter = DefaultLinkFilter("https://example.com")

    worker = DefaultWorker(
        website_url="https://example.com",
        browser=browser,
        link_filter=link_filter,
        depth=2,
    )
    worker.get_data()

    # With depth=2 the worker should not crawl indefinitely
    # get_page_source is called at most once per URL per depth level
    assert browser.get_page_source.call_count <= 3


def test_depth_zero_crawls_only_root():
    """Depth=0 should only visit the root URL."""
    page_source = '<a href="https://example.com/page">link</a>'
    browser = make_browser(page_source)
    link_filter = DefaultLinkFilter("https://example.com")

    worker = DefaultWorker(
        website_url="https://example.com",
        browser=browser,
        link_filter=link_filter,
        depth=0,
    )
    worker.get_data()

    assert browser.get_page_source.call_count == 1
