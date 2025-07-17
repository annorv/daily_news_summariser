# email_utils.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

def send_email(subject, body):
    """Send HTML email with better formatting"""
    try:
        sender = os.getenv("EMAIL_USER")
        recipient = os.getenv("EMAIL_TO")
        password = os.getenv("EMAIL_PASS")
        
        if not all([sender, recipient, password]):
            raise ValueError("Email credentials not properly configured")
        
        # Create multipart message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient
        
        # Convert plain text to HTML for better formatting
        html_body = convert_to_html(body)
        
        # Attach both plain text and HTML versions
        text_part = MIMEText(body, 'plain')
        html_part = MIMEText(html_body, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
            
        logger.info(f"Email sent successfully to {recipient}")
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise

def convert_to_html(text):
    """Convert plain text to HTML with better formatting"""
    # Basic HTML structure
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .article {{
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
            }}
            .title {{
                color: #2c3e50;
                font-size: 1.2em;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .meta {{
                color: #6c757d;
                font-size: 0.9em;
                margin-bottom: 15px;
            }}
            .summary {{
                margin-bottom: 15px;
                text-align: justify;
            }}
            .key-points {{
                background-color: #f8f9fa;
                padding: 15px;
                border-left: 4px solid #007bff;
                margin-bottom: 15px;
            }}
            .source-link {{
                color: #007bff;
                text-decoration: none;
            }}
            .source-link:hover {{
                text-decoration: underline;
            }}
            .separator {{
                border: 0;
                height: 1px;
                background-color: #dee2e6;
                margin: 30px 0;
            }}
            .footer {{
                text-align: center;
                color: #6c757d;
                font-size: 0.9em;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #dee2e6;
            }}
        </style>
    </head>
    <body>
    """
    
    # Process the text content
    lines = text.split('\n')
    in_article = False
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('🤖 AI News Digest'):
            html += f'<div class="header"><h1>{line}</h1></div>\n'
        elif line.startswith('📰 STORY'):
            if in_article:
                html += '</div>\n'
            html += '<div class="article">\n'
            html += f'<div class="title">{line}</div>\n'
            in_article = True
        elif line.startswith('🔗 Source:'):
            url = line.replace('🔗 Source: ', '')
            html += f'<div class="meta">🔗 Source: <a href="{url}" class="source-link">{url}</a></div>\n'
        elif line.startswith('📅 Published:'):
            html += f'<div class="meta">{line}</div>\n'
        elif line.startswith('📝 SUMMARY:'):
            html += '<div class="summary">\n'
        elif line.startswith('🔍 KEY POINTS:'):
            html += '</div>\n<div class="key-points">\n<strong>🔍 KEY POINTS:</strong><br>\n'
        elif line.startswith('• '):
            html += f'{line}<br>\n'
        elif line.startswith('==='):
            if in_article:
                html += '</div>\n</div>\n'
                in_article = False
            html += '<hr class="separator">\n'
        elif line.startswith('Generated on'):
            html += f'<div class="footer">{line}</div>\n'
        elif line and not line.startswith('Today\'s top AI'):
            html += f'<p>{line}</p>\n'
    
    # Close any open article div
    if in_article:
        html += '</div>\n</div>\n'
    
    html += """
    </body>
    </html>
    """
    
    return html