import re
from io import BytesIO

import certifi
import pycurl
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BLOCK_PATTERN = re.compile(
    r"(?i)(cloudflare|attention required|just a moment|access denied|security check|forbidden|verify you are|are you a human|robot check)"
)


def _get_title_with_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)
            page_title = page.title()
            return page_title
        except Exception:
            # We return None so main.py can handle the logging
            return None
        finally:
            browser.close()


def get_title(url):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.FOLLOWLOCATION, True)
    c.setopt(
        c.USERAGENT, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    c.setopt(c.ENCODING, "")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CAINFO, certifi.where())

    try:
        c.perform()
    except pycurl.error:
        c.close()
        return None

    c.close()

    body = buffer.getvalue()
    soup = BeautifulSoup(body, "html.parser")

    if soup.title:
        title_text = soup.title.get_text().strip()

        if title_text and not BLOCK_PATTERN.search(title_text):
            return title_text

    print(f"Static scrape failed or blocked for {url}. Switching to Playwright...")
    return _get_title_with_playwright(url)
