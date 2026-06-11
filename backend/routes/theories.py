from fastapi import APIRouter
from database import get_db
from typing import Optional

router = APIRouter()

@router.get("/")
async def get_theories(
    subreddit: Optional[str] = None,
    sort: str = "hot",
    limit: int = 20,
    skip: int = 0,
    search: Optional[str] = None
):
    db = get_db()
    query = {}
    if subreddit:
        query["subreddit"] = subreddit
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"body": {"$regex": search, "$options": "i"}}
        ]
    sort_field = "scraped_at" if sort == "new" else "upvotes"
    cursor = db["theories"].find(query).sort(sort_field, -1).skip(skip).limit(limit)
    theories = await cursor.to_list(length=limit)
    for t in theories:
        t["_id"] = str(t["_id"])
    return theories

@router.get("/subreddits")
async def get_subreddits():
    db = get_db()
    subreddits = await db["theories"].distinct("subreddit")
    return subreddits

@router.get("/recommend/{theory_id}")
async def get_recommendations(theory_id: str):
    from bson import ObjectId
    db = get_db()
    theory = await db["theories"].find_one({"_id": ObjectId(theory_id)})
    if not theory:
        return []
    cluster = theory.get("cluster_label")
    if not cluster:
        return []
    similar = await db["theories"].find({
        "cluster_label": cluster,
        "_id": {"$ne": ObjectId(theory_id)}
    }).limit(5).to_list(length=5)
    for t in similar:
        t["_id"] = str(t["_id"])
    return similar

@router.post("/summarize/{theory_id}")
async def summarize_theory(theory_id: str):
    import httpx, os
    from bson import ObjectId
    db = get_db()
    theory = await db["theories"].find_one({"_id": ObjectId(theory_id)})
    if not theory:
        return {"summary": "Not found"}
    
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "max_tokens": 200,
                "messages": [{
                    "role": "user",
                    "content": f"Summarize this fan theory in 2-3 sentences:\n\nTitle: {theory['title']}\n\n{theory['body'][:1000]}"
                }]
            },
            timeout=30
        )
        data = res.json()
        print("Groq response:", data)
        if "choices" not in data:
            return {"summary": f"API error: {data.get('error', {}).get('message', 'Unknown error')}"}
        summary = data["choices"][0]["message"]["content"]
    
    await db["theories"].update_one(
        {"_id": ObjectId(theory_id)},
        {"$set": {"summary": summary}}
    )
    return {"summary": summary}
@router.get("/subreddit-counts")
async def get_subreddit_counts():
    db = get_db()
    pipeline = [
        {"$group": {"_id": "$subreddit", "count": {"$sum": 1}}}
    ]
    result = await db["theories"].aggregate(pipeline).to_list(length=100)
    return {item["_id"]: item["count"] for item in result}

@router.get("/trending")
async def get_trending():
    from datetime import datetime, timedelta
    db = get_db()
    since = datetime.utcnow() - timedelta(days=30)
    pipeline = [
        {"$match": {"scraped_at": {"$gte": since}}},
        {"$sort": {"upvotes": -1}},
        {"$limit": 10}
    ]
    result = await db["theories"].aggregate(pipeline).to_list(length=10)
    for t in result:
        t["_id"] = str(t["_id"])
    return result

@router.post("/battle")
async def theory_battle(payload: dict):
    import httpx, os
    from bson import ObjectId
    db = get_db()
    
    id1 = payload.get("theory1_id")
    id2 = payload.get("theory2_id")
    
    t1 = await db["theories"].find_one({"_id": ObjectId(id1)})
    t2 = await db["theories"].find_one({"_id": ObjectId(id2)})
    
    if not t1 or not t2:
        return {"error": "Theory not found"}
    
    prompt = f"""Compare these two fan theories and declare a winner. Be decisive and fun.

Theory 1: {t1['title']}
{t1['body'][:500]}

Theory 2: {t2['title']}
{t2['body'][:500]}

Respond in JSON format:
{{
  "winner": "theory1" or "theory2",
  "verdict": "2-3 sentence explanation",
  "theory1_score": 0-10,
  "theory2_score": 0-10,
  "theory1_strength": "one line",
  "theory2_strength": "one line"
}}"""

    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "max_tokens": 400,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        data = res.json()
        import json
        text = data["choices"][0]["message"]["content"]
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
    
    return {
        "theory1": {"title": t1["title"], "_id": id1},
        "theory2": {"title": t2["title"], "_id": id2},
        **result
    }

@router.post("/generate")
async def generate_theory(payload: dict):
    import httpx, os
    db = get_db()
    subreddit = payload.get("subreddit", "general")
    
    existing = await db["theories"].find({
        "subreddit": subreddit
    }).limit(5).to_list(length=5)
    
    context = "\n\n".join([f"- {t['title']}" for t in existing])
    
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "max_tokens": 300,
                "messages": [{
                    "role": "user",
                    "content": f"Based on these fan theories from r/{subreddit}:\n{context}\n\nGenerate ONE original, creative fan theory for this show/fandom. Give it a catchy title and 3-4 sentences of explanation. Format: Title: ...\n\nTheory: ..."
                }]
            },
            timeout=30
        )
        data = res.json()
        text = data["choices"][0]["message"]["content"]
    
    return {"theory": text, "subreddit": subreddit}