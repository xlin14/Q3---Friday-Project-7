# Import the client libraries
from newsapi import NewsApiClient
import openai
import os # Added for handling API keys securely
from dotenv import load_dotenv # Import dotenv
import requests # For fetching article content from URLs
from bs4 import BeautifulSoup # For parsing the article HTML

# --- NEW: Imports for Email ---
import smtplib # For sending the email
from email.message import EmailMessage # For formatting the email
import ssl # For a secure connection
from datetime import date, timedelta # UPDATED: Added timedelta to calculate past dates
# import certifi # <-- REMOVED: Not needed for the unverified context fix


# --- STEP 1: SETUP ---

# Load API keys from one .env file
# Make sure to install the libraries:
# pip install python-dotenv newsapi-python openai requests beautifulsoup4
# Load variables from the .env file in the same folder
# This file should contain:
# NEWS_API_KEY='your_key_here'
# OPENAI_API_KEY='your_key_here'
# EMAIL_ADDRESS='your.email@gmail.com'
# EMAIL_PASSWORD='your-16-character-app-password'
# RECIPIENT_EMAIL='email.to.send.to@example.com'
load_dotenv()


# --- NewsAPI Setup ---
# We check if the key was loaded. If not, print a specific error and exit.
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
if not NEWS_API_KEY:
    print("--- ERROR: NEWS_API_KEY not found ---")
    print("Please create a file named '.env' in the same folder as main.py.")
    print("Add this line to the .env file:")
    print("NEWS_API_KEY='your_actual_key_from_newsapi_org'")
    print("----------------------------------------")
    exit()


# --- OpenAI Setup ---
# We do the same check for the OpenAI key.
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    print("--- ERROR: OPENAI_API_KEY not found ---")
    print("Please check your '.env' file.")
    print("Add this line to the .env file:")
    print("OPENAI_API_KEY='your_actual_key_from_platform_openai_com'")
    print("----------------------------------------")
    exit()

# --- NEW: Email Setup ---
EMAIL_ADDRESS = os.getenv('SENDER_EMAIL') # UPDATED from 'EMAIL_ADDRESS'
EMAIL_PASSWORD = os.getenv('SENDER_APP_PASSWORD') # UPDATED from 'EMAIL_PASSWORD'
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

if not EMAIL_ADDRESS or not EMAIL_PASSWORD or not RECIPIENT_EMAIL:
    print("--- ERROR: Email credentials not found ---")
    print("Please check your '.env' file.")
    print("It must contain:")
    print("SAN_EMAIL='your.email@gmail.com'") # UPDATED
    print("SENDER_APP_PASSWORD='your-16-character-app-password'") # UPDATED
    print("RECIPIENT_EMAIL='email.to.send.to@example.com'")
    print("----------------------------------------")
    exit()


# Initialize the NewsAPI client
try:
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)
except Exception as e:
    print(f"Error initializing NewsApiClient: {e}")
    print("Your NEWS_API_KEY may be incorrect, even if it was loaded.")
    exit()

# Initialize the OpenAI client
try:
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    client.models.list() # This line tests the key
    print("OpenAI client initialized successfully.")
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    print("Please double-check your OPENAI_API_KEY in the .env file.")
    exit()

# --- Function to Scrape Article Text ---
def get_article_text(url):
    """
    Fetches and extracts the main text content from a news article URL.
    This is a simple scraper and may not work on all websites.
    """
    try:
        # Set a user-agent to pretend to be a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        # Check for successful response
        if response.status_code != 200:
            print(f"  [Scrape Error: Failed to fetch URL with status {response.status_code}]")
            return None

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all paragraph tags <p>
        # This is a simple approach; more complex sites might use <article> or specific IDs
        paragraphs = soup.find_all('p')
        
        if not paragraphs:
            print(f"  [Scrape Error: No <p> tags found. Page might be dynamic or protected.]")
            return None
            
        # Join all paragraph text together
        article_text = ' '.join([p.get_text() for p in paragraphs])
        
        # Basic check for minimal content
        if len(article_text) < 200: # Too short to be a real article
            print(f"  [Scrape Error: Extracted text is too short. Likely a paywall or cookie banner.]")
            return None

        return article_text
        
    except requests.exceptions.RequestException as e:
        print(f"  [Scrape Error: {e}]")
        return None
    except Exception as e:
        print(f"  [Parse Error: {e}]")
        return None

# --- Function to Summarize Text with OpenAI ---
def summarize_text(text_to_summarize):
    """
    Sends text to the OpenAI API and returns a concise summary.
    """
    # Truncate text to avoid exceeding API token limits (e.g., first ~12,000 chars)
    max_length = 12000
    if len(text_to_summarize) > max_length:
        text_to_summarize = text_to_summarize[:max_length]
        
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # You can also use gpt-4 if you have access
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes news articles for a newsletter. Respond with a concise, one-paragraph summary."},
                {"role": "user", "content": f"Please summarize the following article text:\n\n{text_to_summarize}"}
            ]
        )
        summary = response.choices[0].message.content
        return summary.strip()
        
    except Exception as e:
        print(f"  [OpenAI Error: {e}]")
        return "Error: Could not summarize article."


# --- NEW: Function to Send Email (Updated for HTML) ---
def send_email(email_subject, plain_text_body, html_body, recipient_email):
    """
    Connects to the Gmail SMTP server and sends a multipart email
    with both plain-text and HTML versions.
    """
    print(f"\nConnecting to email server to send to {recipient_email}...")
    
    # Create the email message object
    msg = EmailMessage()
    msg['Subject'] = email_subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient_email
    
    # Set the plain-text version (for email clients that don't support HTML)
    msg.set_content(plain_text_body)
    
    # Set the HTML version
    msg.add_alternative(html_body, subtype='html')

    
    # --- FIX 2 for [SSL: CERTIFICATE_VERIFY_FAILED] ---
    # This error: "self-signed certificate in certificate chain"
    # means you are likely on a network with traffic inspection (school, work)
    # or an Antivirus is interfering.
    # This fix tells Python *not* to verify the certificate.
    # It is less secure, but often necessary on managed networks.
    context = ssl._create_unverified_context()
    # --- END FIX ---


    try:
        # Connect to Gmail's SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"--- EMAIL ERROR ---")
        print(f"Error: Unable to send email: {e}")
        print("Please check:")
        print("1. Your EMAIL_ADDRESS and EMAIL_PASSWORD (App Password) are correct in .env")
        print("2. 2-Step Verification and App Passwords are set up correctly in Google.")
    except Exception as e:
        print(f"An unexpected error occurred during email sending: {e}")


# --- STEP 2: MAKE THE API CALL (Updated) ---
print("Fetching latest news for 'technology'...")
try:
    # --- UPDATED: Switched to 'everything' endpoint for a monthly newsletter ---
    # Calculate the date 30 days ago for our search
    thirty_days_ago = (date.today() - timedelta(days=30)).isoformat()
    
    # Use /v2/everything to get top articles from the past month
    # UPDATED: Set page_size=8 and broadened query
    top_headlines = newsapi.get_everything(
        q='(technology OR AI OR programming OR cyber security)', # Broader query
        from_param=thirty_days_ago, # Get articles from this date
        language='en',
        sort_by='popularity', # Get the most popular articles
        page_size=8 # Get 8 articles
    )

    # --- STEP 3: PROCESS, SCRAPE, SUMMARIZE, AND PRINT ---
    if top_headlines['status'] == 'ok':
        
        articles = top_headlines['articles']
        
        # --- NEW: Create lists for plain-text and HTML content ---
        plain_text_summaries = []
        html_summaries = []
        
        if not articles:
            print("No articles found for this topic.")
        else:
            print(f"\nFound {len(articles)} articles. Now scraping and summarizing...\n")
            
            # Loop through each article in the list
            for i, article in enumerate(articles):
                print(f"--- Article {i + 1} ---")
                print(f"Title: {article['title']}")
                print(f"URL: {article['url']}")
                
                # --- NEW SUMMARIZATION LOGIC ---
                print("  Fetching full article text...")
                article_text = get_article_text(article['url'])
                
                if article_text:
                    print("  Summarizing with OpenAI...")
                    summary = summarize_text(article_text)
                    print(f"\n  SUMMARY:\n  {summary}\n")
                    
                    # --- NEW: Add summary to our email lists (Plain Text) ---
                    plain_text_summaries.append(
                        f"Title: {article['title']}\n"
                        f"URL: {article['url']}\n\n"
                        f"Summary: {summary}\n"
                    )
                    
                    # --- NEW: Add summary to our email lists (HTML) ---
                    html_summaries.append(f"""
                    <div style="margin-bottom: 25px; padding-bottom: 25px; border-bottom: 1px solid #eeeeee;">
                        <h2 style="margin: 0 0 10px 0; font-size: 22px; color: #333333;">
                            {article['title']}
                        </h2>
                        <p style="margin: 0 0 15px 0; font-size: 16px; color: #555555; line-height: 1.6;">
                            {summary}
                        </p>
                        <a href="{article['url']}" target="_blank" style="font-size: 14px; color: #007bff; text-decoration: none; font-weight: bold;">
                            Read Full Article &rarr;
                        </a>
                    </div>
                    """)
                    
                else:
                    print("  Skipping summary for this article (could not scrape text).")
                # --- END NEW LOGIC ---
                
                print("-" * 20) # A separator for readability
            
            # --- NEW: After the loop, check if we have summaries to send ---
            if plain_text_summaries:
                # UPDATED: Changed email subject for a monthly newsletter
                today_str = date.today().strftime("%B %Y") # Format as "Month Year"
                email_subject = f"Your Monthly Tech News Summary - {today_str}"
                
                # --- Create the PLAIN-TEXT body ---
                plain_text_body = "Here are your top tech stories:\n\n" + \
                             "\n\n--------------------------\n\n".join(plain_text_summaries)
                
                # --- Create the HTML body ---
                html_body = f"""
                <html>
                <head>
                    <style>
                        body {{
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                            margin: 0;
                            padding: 0;
                            background-color: #f9f9f9;
                        }}
                        .container {{
                            width: 90%;
                            max-width: 650px;
                            margin: 20px auto;
                            padding: 30px;
                            background-color: #ffffff;
                            border: 1px solid #dddddd;
                            border-radius: 8px;
                        }}
                        .header {{
                            font-size: 28px;
                            font-weight: bold;
                            color: #222222;
                            margin: 0 0 30px 0;
                            padding-bottom: 20px;
                            border-bottom: 2px solid #eeeeee;
                        }}
                        .subheader {{
                            font-size: 18px;
                            color: #777777;
                            margin: -20px 0 30px 0;
                        }}
                        a {{
                            color: #007bff;
                            text-decoration: none;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            Your Monthly Tech News
                        </div>
                        <div class="subheader">
                            Top stories for {today_str}
                        </div>
                        {''.join(html_summaries)}
                    </div>
                </body>
                </html>
                """
                
                # Send the email with both versions
                send_email(email_subject, plain_text_body, html_body, RECIPIENT_EMAIL)
            else:
                print("No summaries were generated, skipping email.")

    else:
        print(f"Error fetching news: {top_headlines.get('message')}")

except Exception as e:
    print(f"An error occurred during the API request: {e}")
    print("This could be due to an invalid API key, network issues, or API rate limits.")