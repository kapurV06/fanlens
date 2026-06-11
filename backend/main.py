from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from database import connect_db, close_db

load_dotenv()

app = FastAPI(title="FanLens API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()

@app.get("/")
async def root():
    return {"status": "FanLens API running"}

from routes import theories, scraper, clusters
app.include_router(theories.router, prefix="/api/theories", tags=["theories"])
app.include_router(scraper.router, prefix="/api/scraper", tags=["scraper"])
app.include_router(clusters.router, prefix="/api/clusters", tags=["clusters"])