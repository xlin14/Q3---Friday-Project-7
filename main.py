# Import the client libraries
from newsapi import NewsApiClient
import openai
import os # Added for handling API keys securely
from dotenv import load_dotenv # Import dotenv
import requests # For fetching article content from URLs
from bs4 import BeautifulSoup # For parsing the article HTML

# --- STEP 1: SETUP ---

# Load API keys from one .env file
# Make sure to install the libraries:
# pip install python-dotenv newsapi-python openai requests beautifulsoup4

# Load variables from the .env file in the same folder
# This file should contain:
# NEWS_API_KEY='your_key_here'
# OPENAI_API_KEY='your_key_here'
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

# --- NEW: Function to Scrape Article Text ---
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

# --- NEW: Function to Summarize Text with OpenAI ---
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


# --- STEP 2: MAKE THE API CALL (Updated) ---
print("Fetching latest news for 'technology'...")
try:
    top_headlines = newsapi.get_top_headlines(q='technology',
                                              language='en',
                                              page_size=5) # Reduced to 5 for testing summaries

    # --- STEP 3: PROCESS, SCRAPE, SUMMARIZE, AND PRINT ---
    if top_headlines['status'] == 'ok':
        
        articles = top_headlines['articles']
        
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
                else:
                    print("  Skipping summary for this article (could not scrape text).")
                # --- END NEW LOGIC ---
                
                print("-" * 20) # A separator for readability

    else:
        print(f"Error fetching news: {top_headlines.get('message')}")

except Exception as e:
    print(f"An error occurred during the API request: {e}")
    print("This could be due to an invalid API key, network issues, or API rate limits.")