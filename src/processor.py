import pycurl
import certifi
from io import BytesIO
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def _get_title_with_playwright(url):
    """
    Fallback function that spins up a headless browser to execute JavaScript.
    Used only when standard static scraping fails.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            # 'domcontentloaded' is faster than 'networkidle', but we wait a bit extra for Title updates
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            # Short wait for Single Page Apps (like Twitter) to inject the title tag
            page.wait_for_timeout(2000)
            
            page_title = page.title()
            
            # Format to match BeautifulSoup output style for consistency
            formatted_title = page_title
            return formatted_title
            
        except Exception as e:
            print(f"Playwright failed for {url}: {e}")
            return None
        finally:
            browser.close()


def get_title(url):
    # --- Attempt 1: Fast Static Scrape (pycurl) ---
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.FOLLOWLOCATION, True)
    c.setopt(
        c.USERAGENT, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    # Handle gzip/deflate automatically
    c.setopt(c.ENCODING, "")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CAINFO, certifi.where())
    
    try:
        c.perform()
    except pycurl.error as e:
        print(f"Curl error: {e}")
        c.close()
        return None
        
    c.close()

    body = buffer.getvalue()
    soup = BeautifulSoup(body, "html.parser")

    # --- Check Result ---
    if soup.title and soup.title.string:
        # Success: We got a title cheaply
        print(soup.title.text)
        return soup.title.text
    
    # --- Attempt 2: Slow Dynamic Scrape (Playwright) ---
    else:
        # Failure: The static HTML didn't have a title (likely JS rendered)
        print(f"Static scrape returned None for {url}. Switching to Playwright...")
        title = _get_title_with_playwright(url)
        print(title)
        return title