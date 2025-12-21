import os
import requests
import re
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from urllib.parse import urlparse

def clean_text(text: str) -> str:
    lines = text.splitlines()

    cleaned_lines = []
    short_line_streak = 0

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            short_line_streak = 0
            continue

        word_count = len(line.split())

        # 1️⃣ Drop very short UI/menu lines
        if word_count <= 3:
            short_line_streak += 1
            if short_line_streak >= 2:
                continue
        else:
            short_line_streak = 0

        # 2️⃣ Drop navigation-like lines (Title Case & no punctuation)
        if (
            line.istitle()
            and "." not in line
            and "," not in line
        ):
            continue

        # 3️⃣ Drop button / CTA lines
        if re.fullmatch(r"(read more|learn more|explore|visit website)", line, re.I):
            continue

        # 4️⃣ Drop legal/footer noise
        if re.search(
            r"(copyright|©|all rights reserved|privacy|cookies|disclaimer)",
            line,
            re.I,
        ):
            continue

        cleaned_lines.append(line)

    # Rebuild text
    text = "\n".join(cleaned_lines)

    # 5️⃣ Normalize whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    # 6️⃣ Fix glued sentences
    text = re.sub(r"([a-z])([A-Z][a-z])", r"\1\n\n\2", text)

    return text.strip()



DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": os.environ.get("USER_AGENT", DEFAULT_UA)
}


# Sections we NEVER want
JUNK_SELECTORS = [
    "header",
    "nav",
    "footer",
    "script",
    "style",
    "noscript",
    ".breadcrumbs",
    ".clc-wrp",
    ".header-full-wrp",
    ".footer-wrp",
]

def extract_tata_motors_page(url: str, retries: int = 2) -> list:
    """Extract content from a Tata Motors page with fallback extraction strategies."""
    
    documents = []
    html = None
    
    # Fetch with retries
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            html = response.text
            break
        except requests.RequestException as e:
            if attempt == retries - 1:
                print(f"⚠️ Failed to fetch {url}: {e}")
                return []
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    page_title = soup.find("title")
    page_title = page_title.get_text(strip=True) if page_title else "Untitled"
    
    # Remove junk globally
    for selector in JUNK_SELECTORS:
        for tag in soup.select(selector):
            tag.decompose()
    
    # Primary: Extract from semantic sections
    containers = soup.find_all("section")
    
    # Fallback: If no sections, try article, main, or div.content
    if not containers:
        containers = soup.find_all("article")
    if not containers:
        containers = soup.find_all("main")
    if not containers:
        containers = soup.find_all("div", class_=lambda x: x and ("content" in x or "main" in x or "article" in x))
    
    # If still nothing, extract from body with heading context
    if not containers:
        containers = [soup.find("body")] if soup.find("body") else [soup]
    
    # Extract from each container
    for container in containers:
        if not container:
            continue
        
        # Find the closest heading before this container (section context)
        section_heading = None
        for h in container.find_all(["h1", "h2", "h3"], limit=1):
            txt = h.get_text(" ", strip=True)
            if len(txt.split()) >= 2:
                section_heading = txt
                break
        
        # Extract parts from this container
        parts = []
        
        # Include section heading
        if section_heading:
            parts.append(f"**{section_heading}**")
        
        # Headings (h4, h5 within section)
        for h in container.find_all(["h4", "h5"]):
            txt = h.get_text(" ", strip=True)
            if len(txt.split()) >= 2:
                parts.append(f"## {txt}")
        
        # Paragraphs (lowered threshold from 15 to 10 words)
        for p in container.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if len(txt.split()) >= 10:
                parts.append(txt)
        
        # Extract lists as structured text
        for ul in container.find_all(["ul", "ol"]):
            list_items = []
            for li in ul.find_all("li", recursive=False):
                txt = li.get_text(" ", strip=True)
                if txt and len(txt.split()) >= 3:  # Skip very short list items
                    list_items.append(f"• {txt}")
            if list_items:
                parts.append("\n".join(list_items))
        
        # Skip empty containers
        if len(parts) <= 1:  # Only heading, no content
            continue
        
        text = clean_text("\n\n".join(parts))
        
        # Lowered threshold from 40 to 25 words
        if len(text.split()) < 25:
            continue
        
        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": url,
                    "page_title": page_title,
                    "section": section_heading or "Main Content"
                }
            )
        )
    
    return documents


def normalize_url(url: str) -> str:
    """Normalize URL for deduplication (remove trailing slashes, normalize case)."""
    url = url.rstrip('/')
    return url.lower()


def load_docs(use_cache: bool = False):
    """Load and extract documents from Tata Motors URLs with deduplication and progress printing."""

    raw_urls = [
        "https://www.tatamotors.com/",
        'https://www.tatamotors.com/careers/faqs', 
        'https://www.tatamotors.com/corporate-responsibility/planet-resilience/', 
        'https://www.tatamotors.com/careers/life-at-tml/', 
        'https://www.tatamotors.com/newsroom/thought-leadership', 
        'https://www.tatamotors.com/careers', 
        'https://www.tatamotors.com/careers/kaushalya-earn-learn-program/', 
        'https://www.tatamotors.com/corporate-responsibility/planet-resilience', 
        'https://www.tatamotors.com/corporate-responsibility/governance/', 
        'https://www.tatamotors.com/careers/openings/', 
        'https://www.tatamotors.com/open-source-license-disclosure', 
        'https://www.tatamotors.com/blog/a-smarter-vision-for-safer-roads-decoding-advanced-driver-assistance-systems-3/', 
        'https://www.tatamotors.com/blog/new-era-for-indias-cv-landscape/', 
        'https://www.tatamotors.com/corporate-responsibility', 
        'https://www.tatamotors.com/legal-disclaimer', 
        'https://www.tatamotors.com/newsroom', 
        'https://www.tatamotors.com/careers/life-at-tml', 
        'https://www.tatamotors.com/blog/defining-new-mobility-for-india/', 
        'https://www.tatamotors.com/blog/2021-recovery-ahead/', 
        'https://www.tatamotors.com/organisation/our-history/',  
        'https://www.tatamotors.com/csr-archive', 
        'https://www.tatamotors.com', 
        'https://www.tatamotors.com/corporate-responsibility/governance', 
        'https://www.tatamotors.com/contact-us', 
        'https://www.tatamotors.com/blog/developing-software-on-wheels-seamless-technologies-for-the-vehicles-of-tomorrow-2/', 
        'https://www.tatamotors.com/corporate-responsibility/', 
        'https://www.tatamotors.com/blog/ownership-in-logistics-newer-opportunities-for-india-in-a-post-covid-world/',
        'https://www.tatamotors.com/future-of-mobility/', 
        'https://www.tatamotors.com/future-of-mobility', 
        'https://www.tatamotors.com/careers/', 
        'https://www.tatamotors.com/corporate-responsibility/working-with-communities', 
        'https://www.tatamotors.com/careers/kaushalya-earn-learn-program', 
        'https://www.tatamotors.com/careers/openings', 
        'https://www.tatamotors.com/corporate-responsibility/working-with-communities/'
    ]

    print(f"🔹 Raw URLs provided: {len(raw_urls)}")

    # Deduplicate and normalize URLs
    unique_urls = {}
    for url in raw_urls:
        normalized = normalize_url(url)
        if normalized not in unique_urls:
            unique_urls[normalized] = url

    urls = list(unique_urls.values())

    print(f"📌 Deduplication complete: {len(raw_urls)} → {len(urls)} unique URLs\n")

    docs = []

    total = len(urls)
    for i, url in enumerate(urls, 1):
        print(f"➡️  [{i}/{total}] Fetching & extracting:")
        print(f"    🌐 {url}")

        before = len(docs)
        extracted = extract_tata_motors_page(url)
        docs.extend(extracted)
        after = len(docs)

        print(f"    📄 Extracted {len(extracted)} documents")
        print(f"    📊 Total documents so far: {after}\n")

    print(f"🎉 Done!")
    print(f"📚 Total documents extracted: {len(docs)}")

    return docs
