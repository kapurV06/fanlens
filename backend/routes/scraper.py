import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import APIRouter, BackgroundTasks
from services.reddit_scraper import scrape_subreddit

router = APIRouter()

@router.post("/scrape/{subreddit}")
async def trigger_scrape(subreddit: str, background_tasks: BackgroundTasks, limit: int = 50):
    background_tasks.add_task(scrape_subreddit, subreddit, limit)
    return {"message": f"Scraping r/{subreddit} in background"}

@router.delete("/subreddit/{name}")
async def delete_subreddit(name: str):
    from database import get_db
    db = get_db()
    result = await db["theories"].delete_many({"subreddit": name})
    return {"deleted": result.deleted_count}