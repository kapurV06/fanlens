from fastapi import APIRouter
from database import get_db

router = APIRouter()

@router.get("/")
async def get_clusters():
    db = get_db()
    pipeline = [
        {"$match": {"cluster_label": {"$ne": None}}},
        {"$group": {"_id": "$cluster_label", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    result = await db["theories"].aggregate(pipeline).to_list(length=10)
    return result
