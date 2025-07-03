from summariser import summarise_headlines
from email_utils import send_email
import feedparser
from datetime import datetime

def fetch_ai_news():
    feed_url = "https://news.google.com/rss/search?q=artificial+intelligence"
    feed = feedparser.parse(feed_url)
    headlines = [entry.title for entry in feed.entries[:5]]  # Top 5
    return headlines

def main():
    headlines = fetch_ai_news()
    summary = summarise_headlines(headlines)

    today = datetime.now().strftime('%B %d, %Y')
    subject = f"AI News Summary – {today}"
    body = f"📰 Today's Top AI Headlines:\n\n" + "\n".join(f"- {s}" for s in summary)

    send_email(subject, body)

if __name__ == "__main__":
    main()
