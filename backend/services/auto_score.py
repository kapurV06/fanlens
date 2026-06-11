HIGH_CONFIDENCE_KEYWORDS = [
    "evidence", "proof", "confirmed", "theory", "foreshadow", "symbolism",
    "detail", "notice", "subtle", "hidden", "clue", "parallel", "connection",
    "pattern", "analysis", "breakdown", "explained", "actually", "realize"
]

MEDIUM_CONFIDENCE_KEYWORDS = [
    "think", "believe", "maybe", "possibly", "could", "might", "opinion",
    "suggest", "hint", "imply", "seem", "appear", "wonder", "guess"
]

LOW_CONFIDENCE_KEYWORDS = [
    "random", "crazy", "wild", "unpopular", "controversial", "hot take",
    "just me", "am i the only", "anyone else", "no one talks about"
]

def auto_score_confidence(title: str, body: str) -> str:
    text = (title + " " + body).lower()
    
    high = sum(1 for kw in HIGH_CONFIDENCE_KEYWORDS if kw in text)
    medium = sum(1 for kw in MEDIUM_CONFIDENCE_KEYWORDS if kw in text)
    low = sum(1 for kw in LOW_CONFIDENCE_KEYWORDS if kw in text)
    
    if high >= 3:
        return "high"
    elif high >= 1 or medium >= 3:
        return "medium"
    elif low >= 1:
        return "low"
    else:
        return "medium"