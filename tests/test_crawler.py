import subprocess
import time
from http.client import HTTPConnection
from pathlib import Path

import pytest

from src.search import Searcher


@pytest.fixture(scope="session")
def static_server():
    process = subprocess.Popen(
        ["python", "-m", "http.server", "8080", "--directory", "/Users/oscar/Projects/ai-daily-podcast/resources/"],
        stdout=subprocess.PIPE
    )

    retries = 5
    while retries > 0:
        conn = HTTPConnection("localhost:8080")
        try:
            conn.request("HEAD", "/")
            response = conn.getresponse()
            if response is not None:
                break
        except ConnectionRefusedError:
            time.sleep(1)
            retries -= 1
    if not retries:
        raise RuntimeError("Can't start static server")

    yield process


@pytest.mark.asyncio
async def test_should_crawl_links_from_given_url(static_server):
    dummy_project_root_dir: Path = Path("dummy_path")

    crawler = Searcher(project_dir=dummy_project_root_dir)

    source = "http://localhost:8080/rtve_main_page_test_case.html"
    pattern_filter = r"^https://www.rtve.es/noticias/\d{8}/[a-zA-Z0-9\-]+/\d+\.shtml$"
    crawled_links = await crawler.get_news_link_from(source, pattern_filter)

    static_server.terminate()

    assert len(crawled_links) > 0

