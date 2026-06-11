from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Theory(BaseModel):
    reddit_id: str
    title: str
    body: str
    summary: Optional[str] = None
    subreddit: str
    upvotes: int
    comment_count: int
    author: str
    url: str
    topics: List[str] = []
    cluster_label: Optional[str] = None
    confidence: Optional[str] = None
    toxicity_score: Optional[float] = None
    bias_score: Optional[float] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
