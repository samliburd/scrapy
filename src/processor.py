import os
import re
from io import BytesIO
from urllib.parse import urlparse

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
            # Reduced timeout to 10s to prevent long hangs on heavy SPAs
            page.goto(url, wait_until="domcontentloaded", timeout=10000)
            page.wait_for_timeout(2000)
            page_title = page.title()
            return page_title
        except Exception:
            return None
        finally:
            browser.close()


def get_title(url):
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.FOLLOWLOCATION, True)
    c.setopt(
        c.USERAGENT, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    c.setopt(c.ENCODING, "")
    c.setopt(c.CAINFO, certifi.where())

    # --- SAFETY FIX: Add Timeouts ---
    # CONNECTTIMEOUT: Max time allowed to establish connection
    c.setopt(c.CONNECTTIMEOUT, 5)
    # TIMEOUT: Max time allowed for the entire operation
    c.setopt(c.TIMEOUT, 10)

    # --- STEP 1: HEAD Request (Check Content-Type) ---
    c.setopt(c.NOBODY, True)

    try:
        c.perform()
    except pycurl.error:
        c.close()
        return None

    content_type = c.getinfo(c.CONTENT_TYPE)

    if content_type is None or "text/html" not in content_type.lower():
        c.close()
        parsed_path = urlparse(url).path
        filename = os.path.basename(parsed_path)
        return filename if filename else "Index / Unknown File"

    # --- STEP 2: GET Request (Download HTML) ---
    c.setopt(c.HTTPGET, True)
    
    buffer = BytesIO()
    c.setopt(c.WRITEDATA, buffer)

    try:
        c.perform()
    except pycurl.error:
        # If the download times out or fails, we abort
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
