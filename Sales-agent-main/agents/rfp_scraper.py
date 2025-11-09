# agents/rfp_scraper.py
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from dateutil import parser as dateparser
import re
import time

# Utility: try to parse any date string
def parse_date(date_str):
    if not date_str:
        return None
    try:
        return dateparser.parse(date_str, fuzzy=True).strftime("%Y-%m-%d")
    except Exception:
        return None


# Utility: extract date-like strings from HTML text
def extract_possible_dates(text):
    date_patterns = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4}\b",
    ]
    for pattern in date_patterns:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        if matches:
            return parse_date(matches[0])
    return None


def scrape_html_page(url):
    """Scrape an HTML page using requests + BeautifulSoup."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (SalesAgentBot/1.0)"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        rfps = []
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            if not text:
                continue

            # Look for tender-like words
            if re.search(r"tender|rfp|bid|procurement|contract", text, re.IGNORECASE):
                href = a["href"]
                link = href if href.startswith("http") else requests.compat.urljoin(url, href)

                # Try to find nearby date text
                parent_text = a.find_parent().get_text(" ", strip=True) if a.find_parent() else ""
                due_date = extract_possible_dates(parent_text)

                rfps.append({
                    "title": text[:200],
                    "url": link,
                    "due_date": due_date
                })

        return rfps
    except Exception as e:
        print(f"[WARN] Failed to scrape {url}: {e}")
        return []


def scrape_js_page(url):
    """Scrape pages requiring JS rendering using requests_html."""
    try:
        session = HTMLSession()
        resp = session.get(url)
        resp.html.render(timeout=25, sleep=2)
        soup = BeautifulSoup(resp.html.html, "html.parser")

        rfps = []
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            if re.search(r"tender|rfp|bid|procurement|contract", text, re.IGNORECASE):
                href = a["href"]
                link = href if href.startswith("http") else requests.compat.urljoin(url, href)
                parent_text = a.find_parent().get_text(" ", strip=True) if a.find_parent() else ""
                due_date = extract_possible_dates(parent_text)

                rfps.append({
                    "title": text[:200],
                    "url": link,
                    "due_date": due_date
                })
        return rfps
    except Exception as e:
        print(f"[WARN] JS scrape failed for {url}: {e}")
        return []


def scrape_urls(url_list):
    """Master function that scrapes multiple URLs."""
    all_rfps = []
    for url in url_list:
        print(f"🔍 Scraping: {url}")
        rfps = scrape_html_page(url)

        # If too few found, try JS-rendered version
        if len(rfps) < 3:
            rfps = scrape_js_page(url)

        print(f"  → Found {len(rfps)} RFP links")
        all_rfps.extend(rfps)

        # Small delay to avoid rate limiting
        time.sleep(1.5)

    # Remove duplicates by title or URL
    unique = []
    seen = set()
    for r in all_rfps:
        key = (r["title"], r["url"])
        if key not in seen:
            seen.add(key)
            unique.append(r)

    return unique
