import sqlite3
import feedparser
from datetime import datetime, timezone, timedelta
from typing import List, Dict

DB_NAME = "seen_news.db"

RSS_SOURCES = {
    "TechCrunch_AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "Toms_Hardware": "https://www.tomshardware.com/feeds/all",
    "The_Verge_Tech": "https://www.theverge.com/rss/tech/index.xml",
    "AI_Tech_Radar": (
        "https://news.google.com/rss/search?"
        "q=(NVIDIA+OR+OpenAI+OR+Gemini+OR+Claude+OR+DeepSeek+OR+Kimi+OR+ASUS+OR+Dell+OR+Microsoft)+when:1d"
        "&hl=en-US&gl=US&ceid=US:en"
    )
}

TARGET_KEYWORDS = [
    "nvidia", "intel", "amd", "microsoft", "windows", "apple", "dell", "asus",
    "openai", "chatgpt", "gemini", "claude", "anthropic", "deepseek", "kimi",
    "moonshot", "qwen", "ai", "llm", "gpu", "rtx"
]

# --- قسم الداتابيس (لمنع تكرار الأخبار) ---
def init_db():
    """إنشاء جدول بسيط يحفظ روابط الأخبار اللي مرت على الإيجنت"""
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS seen_articles (
                link TEXT PRIMARY KEY,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def is_already_seen(link: str) -> bool:
    """هل هذا الخبر فحصناه أو دزيناه سابقاً؟"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("SELECT 1 FROM seen_articles WHERE link = ?", (link,))
        return cursor.fetchone() is not None

def mark_as_seen(link: str):
    """تسجيل الخبر بالداتابيس حتى ما ينعاد مرة ثانية"""
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT OR IGNORE INTO seen_articles (link) VALUES (?)", (link,))

# --- قسم الفلترة الأولية والسحب ---
def is_relevant(title: str, summary: str) -> bool:
    content = f"{title} {summary}".lower()
    return any(keyword in content for keyword in TARGET_KEYWORDS)

def is_from_today(entry: dict) -> bool:
    """يتأكد أن الخبر نزل خلال آخر 24 ساعة فقط"""
    time_struct = entry.get("published_parsed") or entry.get("updated_parsed")
    if not time_struct:
        return False
    published_dt = datetime(*time_struct[:6], tzinfo=timezone.utc)
    now_dt = datetime.now(timezone.utc)
    return published_dt >= (now_dt - timedelta(days=1))

def get_new_articles() -> List[Dict]:
    """الدالة الرئيسية اللي يستدعيها الإيجنت"""
    init_db()
    new_articles = []

    for source_name, url in RSS_SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            link = entry.get("link", "")
            title = entry.get("title", "")
            summary = entry.get("summary", "")

            # 1. إذا الخبر مو مال اليوم ⬅️ اعبره
            if not is_from_today(entry):
                continue

            # 2. إذا الخبر موجود بالداتابيس (دازينه قبل) ⬅️ اعبره
            if is_already_seen(link):
                continue

            # 3. إذا يخص الشركات اللي نهتم بيها ⬅️ ضيفه للقائمة
            if is_relevant(title, summary):
                new_articles.append({
                    "source": source_name,
                    "title": title,
                    "summary": summary,
                    "link": link
                })

    return new_articles