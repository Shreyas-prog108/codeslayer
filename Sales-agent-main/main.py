# main.py
import json
from datetime import datetime, timedelta
from agents.rfp_scraper import scrape_urls
from agents.sales_agent import (
    filter_due_within,
    summarize_rfps,
    select_best_rfp
)

# 🌍 List of Government + Non-Government Tender & RFP Sources
URLS = [
    # 🇮🇳 Indian Government Portals
    "https://etenders.gov.in/eprocure/app",
    "https://tenders.gov.in",
    "https://gem.gov.in/tenders",
    "https://eproc.rajasthan.gov.in/nicgep/app",
    "https://mahatenders.gov.in/nicgep/app",
    "https://tenderwizard.com",
    "https://eprocure.gov.in/cppp/",
    "https://www.gepnic.gov.in/",
    "https://demoeproc.nic.in/epublish/app?page=FrontEndParticipatingSites&service=page",

    # 🌎 Global / Development Organizations
    "https://www.dgmarket.com/",
    "https://www.tendersinfo.com/tenders-by-country.php",
    "https://www.biddetail.com/",
    "https://www.tendersontime.com/",
    "https://www.tender247.com/",
    "https://www.simap.ch/",
    "https://prozorro.gov.ua/",
    "https://www.gebiz.gov.sg/",
    "https://www.worldbank.org/en/projects-operations/procurement",
    "https://commission.europa.eu/funding-tenders/tools-public-buyers/public-procurement-eu-countries_en",
    "https://www.uhapex.uh.edu/images/ptac/List%20%20of%20Procurement%20Websites%20updated.pdf",
    "https://www.tenderimpulse.com/tender-by-country",
    "https://www.afdb.org/en/projects-and-operations/procurement",
    "https://www.adb.org/projects/tenders",
    "https://www.ungm.org/Public/Notice",
    "https://tenders.unops.org/",
    "https://www.undp.org/procurement",
    "https://www.devex.com/tenders",

    # 💼 Corporate / Private / Aggregator Sites
    "https://www.rfpdb.com",
    "https://www.findrfp.com",
    "https://www.rfpalert.com",
    "https://www.bidnet.com",
    "https://www.opentenders.com",
    "https://www.globaltenders.com",
    "https://www.bidassist.com",
]

def main():
    print("\n🤖 Offline Sales Agent System (Ollama) — Fetch, Summarize, Select, Respond\n")

    # Step 1️⃣: Scrape
    print("🔍 Scraping sources...")
    rfps = scrape_urls(URLS)
    print(f"✅ Scraped total {len(rfps)} RFP entries.\n")

    if not rfps or not isinstance(rfps, list):
        print("❌ No RFP entries found or invalid format returned by scraper.")
        return

    # Save all raw results
    with open("rfp_all_results.json", "w", encoding="utf-8") as f:
        json.dump(rfps, f, ensure_ascii=False, indent=2)

    # Step 2️⃣: Filter due within 90 days
    print("📅 Filtering RFPs due within 90 days...")
    candidates = filter_due_within(rfps, days=90)
    print(f"🕒 Found {len(candidates)} candidates.\n")

    with open("rfp_candidates.json", "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)

    if not candidates:
        print("⚠️ No RFPs found within next 90 days. Try adjusting filters or adding more sources.")
        return

    # Step 3️⃣: Summarize RFPs (Ollama)
    print("🧠 Summarizing candidate RFPs with Ollama (please wait)...")
    summarized = summarize_rfps(candidates)
    with open("rfp_summaries.json", "w", encoding="utf-8") as f:
        json.dump(summarized, f, ensure_ascii=False, indent=2)
    print("📝 Saved summaries → rfp_summaries.json\n")

    # Step 4️⃣: Select best RFP
    print("🎯 Selecting best RFP for response...")
    selected = select_best_rfp(summarized)

    if not selected:
        print("⚠️ No best RFP could be determined.")
        return

    with open("selected_rfp.json", "w", encoding="utf-8") as f:
        json.dump(selected, f, ensure_ascii=False, indent=2)

    print(f"✅ Selected RFP saved → selected_rfp.json")
    print(f"\n📌 Title: {selected.get('title')}")
    print(f"🕓 Due: {selected.get('due_date')}")
    print(f"💡 Reason: {selected.get('selection_reason', 'Auto-selected based on due date')}")
    print("\n🚀 Hand off this selected RFP to your Main Agent next for drafting the response.\n")

if __name__ == "__main__":
    main()
