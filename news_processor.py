# news_processor.py
import feedparser
import newspaper
from transformers import pipeline
from datetime import datetime
import logging
import time
import re

logger = logging.getLogger(__name__)

class NewsProcessor:
    def __init__(self):
        # Initialise summarisation pipeline
        try:
            self.summarizer = pipeline(
                "summarisation", 
                model="facebook/bart-large-cnn",  # Better model for news summarisation
                tokenizer="facebook/bart-large-cnn"
            )
            logger.info("Summarisation model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load summarisation model: {e}")
            # Fallback to smaller model
            self.summarizer = pipeline("summarisation", model="t5-small", tokenizer="t5-small")
    
    def fetch_ai_news(self, num_articles=5):
        """Fetch AI news from multiple sources"""
        articles = []
        
        # Multiple RSS feeds for better coverage
        feeds = [
            "https://news.google.com/rss/search?q=artificial+intelligence&hl=en&gl=US&ceid=US:en",
            "https://techcrunch.com/tag/ai/feed/",
            "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
            "https://feeds.feedburner.com/oreilly/radar",
        ]
        
        for feed_url in feeds:
            try:
                logger.info(f"Fetching from: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:num_articles]:
                    article_data = {
                        'title': entry.title,
                        'url': entry.link,
                        'published': getattr(entry, 'published', 'Unknown'),
                        'summary': getattr(entry, 'summary', ''),
                        'source': feed.feed.get('title', 'Unknown Source')
                    }
                    articles.append(article_data)
                    
                    # Limit total articles
                    if len(articles) >= num_articles * 2:
                        break
                        
            except Exception as e:
                logger.error(f"Error fetching from {feed_url}: {e}")
                continue
        
        # Remove duplicates based on title similarity
        unique_articles = self._remove_duplicates(articles)
        
        return unique_articles[:num_articles]
    
    def _remove_duplicates(self, articles):
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            # Normalise title for comparison
            normalized_title = re.sub(r'[^\w\s]', '', article['title'].lower())
            
            # Check if we've seen a similar title
            is_duplicate = False
            for seen_title in seen_titles:
                if self._calculate_similarity(normalized_title, seen_title) > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
                seen_titles.add(normalized_title)
        
        return unique_articles
    
    def _calculate_similarity(self, text1, text2):
        """Simple similarity calculation"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0
    
    def extract_article_content(self, url):
        """Extract full article content from URL"""
        try:
            article = newspaper.Article(url)
            article.download()
            article.parse()
            
            return {
                'text': article.text,
                'authors': article.authors,
                'publish_date': article.publish_date,
                'top_image': article.top_image
            }
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def generate_detailed_summaries(self, articles):
        """Generate detailed summaries for each article"""
        detailed_summaries = []
        
        for i, article in enumerate(articles, 1):
            logger.info(f"Processing article {i}/{len(articles)}: {article['title']}")
            
            try:
                # Extract full article content
                content = self.extract_article_content(article['url'])
                
                if content and content['text']:
                    # Use full article text for summarisation
                    text_to_summarize = content['text']
                else:
                    # Fallback to RSS summary
                    text_to_summarize = article['summary']
                
                # Generate detailed summary
                detailed_summary = self._create_detailed_summary(text_to_summarize)
                
                # Extract key points
                key_points = self._extract_key_points(text_to_summarize)
                
                summary_data = {
                    'title': article['title'],
                    'source_url': article['url'],
                    'published': self._format_date(article['published']),
                    'detailed_summary': detailed_summary,
                    'key_points': key_points,
                    'source': article['source']
                }
                
                detailed_summaries.append(summary_data)
                
                # Add delay to avoid overwhelming servers
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing article {article['title']}: {e}")
                # Add a minimal summary even if processing fails
                detailed_summaries.append({
                    'title': article['title'],
                    'source_url': article['url'],
                    'published': self._format_date(article['published']),
                    'detailed_summary': article.get('summary', 'Summary unavailable'),
                    'key_points': '• Content extraction failed',
                    'source': article['source']
                })
        
        return detailed_summaries
    
    def _create_detailed_summary(self, text):
        """Create a detailed summary of the article"""
        if not text or len(text.strip()) < 100:
            return "Detailed summary unavailable - insufficient content."
        
        try:
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            # Split into chunks if text is too long
            max_chunk_length = 1000
            if len(cleaned_text) > max_chunk_length:
                chunks = [cleaned_text[i:i+max_chunk_length] 
                         for i in range(0, len(cleaned_text), max_chunk_length)]
                
                summaries = []
                for chunk in chunks[:3]:  # Limit to 3 chunks
                    summary = self.summarizer(chunk, 
                                            max_length=150, 
                                            min_length=50, 
                                            do_sample=False)
                    summaries.append(summary[0]['summary_text'])
                
                return ' '.join(summaries)
            else:
                summary = self.summarizer(cleaned_text, 
                                        max_length=200, 
                                        min_length=100, 
                                        do_sample=False)
                return summary[0]['summary_text']
                
        except Exception as e:
            logger.error(f"Error creating detailed summary: {e}")
            return "Detailed summary generation failed."
    
    def _extract_key_points(self, text):
        """Extract key points from the article"""
        if not text or len(text.strip()) < 50:
            return "• Key points unavailable"
        
        try:
            # Simple key point extraction based on sentences
            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
            
            # Score sentences based on AI-related keywords
            ai_keywords = ['artificial intelligence', 'ai', 'machine learning', 'deep learning', 
                          'neural network', 'automation', 'algorithm', 'chatbot', 'llm', 
                          'generative ai', 'openai', 'anthropic', 'google', 'microsoft']
            
            scored_sentences = []
            for sentence in sentences[:20]:  # Limit to first 20 sentences
                score = 0
                sentence_lower = sentence.lower()
                for keyword in ai_keywords:
                    if keyword in sentence_lower:
                        score += 1
                
                if score > 0:
                    scored_sentences.append((sentence, score))
            
            # Sort by score and take top 3-4
            scored_sentences.sort(key=lambda x: x[1], reverse=True)
            key_points = [sentence[0] for sentence in scored_sentences[:4]]
            
            if key_points:
                return '\n'.join(f"• {point}" for point in key_points)
            else:
                return "• Key points extraction unavailable"
                
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return "• Key points extraction failed"
    
    def _clean_text(self, text):
        """Clean text for better processing"""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere
        text = re.sub(r'[^\w\s.,!?;:]', '', text)
        return text.strip()
    
    def _format_date(self, date_str):
        """Format date string for better readability"""
        if not date_str or date_str == 'Unknown':
            return 'Unknown'
        
        try:
            # Parse common date formats
            for fmt in ['%a, %d %b %Y %H:%M:%S %Z', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%B %d, %Y')
                except ValueError:
                    continue
            
            # If parsing fails, return original
            return date_str
            
        except Exception:
            return date_str