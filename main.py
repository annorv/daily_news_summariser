# main.py
from news_processor import NewsProcessor
from email_utils import send_email
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    try:
        # Initialise news processor
        processor = NewsProcessor()
        
        # Fetch and process news articles
        logger.info("Fetching AI news articles...")
        articles = processor.fetch_ai_news()
        
        if not articles:
            logger.warning("No articles found")
            return
        
        logger.info(f"Found {len(articles)} articles, processing...")
        
        # Generate detailed summaries
        detailed_summaries = processor.generate_detailed_summaries(articles)
        
        # Create email content
        today = datetime.now().strftime('%B %d, %Y')
        subject = f"🤖 AI News Digest - {today}"
        
        # Format email body
        body = f"""
🤖 AI News Digest - {today}

Today's top AI developments with detailed analysis:

{'='*60}

"""
        
        for i, summary in enumerate(detailed_summaries, 1):
            body += f"""
📰 STORY {i}: {summary['title']}

🔗 Source: {summary['source_url']}
📅 Published: {summary['published']}

📝 SUMMARY:
{summary['detailed_summary']}

🔍 KEY POINTS:
{summary['key_points']}

{'='*60}

"""
        
        body += f"""
Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Powered by your AI News Bot 🤖
"""
        
        # Send email
        send_email(subject, body)
        logger.info("Email sent successfully!")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()