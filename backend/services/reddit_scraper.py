import httpx
import xml.etree.ElementTree as ET
from database import get_db
from datetime import datetime
from services.auto_score import auto_score_confidence

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

async def scrape_subreddit(subreddit_name: str, limit: int = 50):
    db = get_db()
    url = f"https://www.reddit.com/r/{subreddit_name}/hot.rss?limit={limit}"
    
    async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
        response = await client.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch r/{subreddit_name}: {response.status_code}")
            return 0
    
    root = ET.fromstring(response.text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", ns)
    
    scraped = 0
    for entry in entries:
        title = entry.find("atom:title", ns)
        content = entry.find("atom:content", ns)
        link = entry.find("atom:link", ns)
        author = entry.find("atom:author/atom:name", ns)
        entry_id = entry.find("atom:id", ns)
        
        if title is None or content is None:
            continue
        
        body = content.text or ""
        if len(body) < 100:
            continue
        
        reddit_id = entry_id.text.split("_")[-1] if entry_id is not None else ""
        existing = await db["theories"].find_one({"reddit_id": reddit_id})
        if existing:
            continue
        
        title_text = title.text or ""
        confidence = auto_score_confidence(title_text, body)
        
        theory = {
            "reddit_id": reddit_id,
            "title": title_text,
            "body": body[:2000],
            "subreddit": subreddit_name,
            "upvotes": 0,
            "comment_count": 0,
            "author": author.text if author is not None else "[deleted]",
            "url": link.get("href", "") if link is not None else "",
            "topics": [],
            "cluster_label": None,
            "confidence": confidence,
            "toxicity_score": None,
            "bias_score": None,
            "scraped_at": datetime.utcnow()
        }
        await db["theories"].insert_one(theory)
        scraped += 1
    
    print(f"Scraped {scraped} new theories from r/{subreddit_name}")
    return scraped