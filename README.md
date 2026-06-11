# FanLens

A tool that scrapes fan theories from Reddit, clusters them by topic using NLP, and lets you explore them through a clean dashboard. Built this because I wanted a way to actually browse fan theories without scrolling through hundreds of unrelated posts.

## What it does

- Pulls posts from any subreddit (r/FanTheories, r/breakingbad, r/supernatural, etc.)
- Groups similar theories together using BERTopic clustering
- Scores each theory's "confidence" based on language patterns (is it backed by evidence or just a hot take?)
- Generates AI summaries for long theory posts using Groq's Llama models
- Suggests similar theories based on topic clusters
- Has an AI theory generator that creates original fan theories based on existing discussion patterns
- Tracks trending theories from the last 30 days

## Stack

**Backend:** FastAPI + MongoDB Atlas (Motor for async)
**Frontend:** Vue 3 + Vite
**NLP:** BERTopic, sentence-transformers (run via Colab since training needs more compute than my laptop has)
**LLM:** Groq API (Llama 3.1) for summarization and theory generation

## Why these choices

- Used Reddit's RSS feeds instead of PRAW because Reddit's API requires app registration which kept failing with reCAPTCHA issues. RSS works without auth and is good enough for read-only scraping.
- MongoDB over SQL because theory data is pretty unstructured (varying lengths, optional fields like cluster labels that get added later)
- Groq instead of OpenAI/Anthropic mainly because it's free and fast enough for this use case

## Running it locally

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

You'll need a `.env` file in `backend/` with:
```
MONGODB_URI=your_mongodb_connection_string
GROQ_API_KEY=your_groq_key
```

## NLP Pipeline

The clustering and confidence scoring happens in a separate Colab notebook (`fanlens_nlp.ipynb`) since it needs sentence-transformers and BERTopic which are too heavy to run on a low-spec machine. New subreddits get a basic keyword-based confidence score automatically when scraped, and can be re-processed through the notebook for better topic clustering.

## Known limitations

- Upvote/comment counts are always 0 since RSS feeds don't expose this data (would need authenticated API access to fix)
- Confidence scoring is keyword-based as a fallback — proper BERTopic clustering needs to be run manually via Colab
- No pagination caching, so switching filters re-fetches from scratch

## Screenshots

<img width="1895" height="917" alt="image" src="https://github.com/user-attachments/assets/8983f543-a0c9-4269-81cd-7b62739a7c75" />
<img width="1882" height="901" alt="image" src="https://github.com/user-attachments/assets/bdbb8e42-c188-4ef3-8187-be35b5e19ef5" />
<img width="1893" height="911" alt="image" src="https://github.com/user-attachments/assets/7f01167e-d61c-482e-ace3-c990292c40bb" />



---

Built as a personal project to explore NLP clustering + LLM integration in a full-stack app.
