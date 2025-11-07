# Import the client libraries
from newsapi import NewsApiClient
import openai
import os # Added for handling API keys securely
from dotenv import load_dotenv # Import dotenv

# --- STEP 1: SETUP ---

# Load API keys from .env files
# Make sure to install the library: pip install python-dotenv

# Load the NewsAPI key from your "NewsAPI.env" file
# This file should contain a line like: NEWS_API_KEY='your_key_here'
load_dotenv(dotenv_path='NewsAPI.env')

# Load the OpenAI API key from your "fetch news api key.env" file
# This file should contain a line like: OPENAI_API_KEY='your_key_here'
load_dotenv(dotenv_path='fetch news api key.env')


# --- NewsAPI Setup ---
# It's best practice to set API keys as environment variables
# rather than hard-coding them.
# You can set this in your terminal: export NEWS_API_KEY='your_key_here'
# The code will try to get it from the environment, or fall back to the placeholder.
NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'YOUR_NEWS_API_KEY_HERE')

# --- OpenAI Setup ---
# You can set this in your terminal: export OPENAI_API_KEY='your_key_here'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY_HERE')


# Initialize the NewsAPI client
try:
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)
except Exception as e:
    print(f"Error initializing NewsApiClient: {e}")
    print("Please make sure you have set your NEWS_API_KEY correctly.")
    exit()

# Initialize the OpenAI client
try:
    # Set the API key for the openai library
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    # Let's test the key with a simple, non-token-using call to list models
    # This confirms the key is valid before we proceed.
    client.models.list()
    print("OpenAI client initialized successfully.")
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    print("Please make sure you have set your OPENAI_API_KEY correctly and installed the 'openai' library (pip install openai).")
    exit()


# --- STEP 2: MAKE THE API CALL ---
# We will fetch the top headlines for a specific topic.
# You can change 'technology' to any topic you want (e.g., 'business', 'AI', 'sports').
# We'll also specify the language as English ('en').
print("Fetching latest news for 'technology'...")
try:
    top_headlines = newsapi.get_top_headlines(q='technology',
                                              language='en',
                                              page_size=10) # Get 10 articles

    # --- STEP 3: PROCESS THE RESPONSE AND PRINT ---
    # The API response is a dictionary. We check the 'status' key to see if it worked.
    if top_headlines['status'] == 'ok':
        
        # The articles are in a list under the 'articles' key
        articles = top_headlines['articles']
        
        if not articles:
            print("No articles found for this topic.")
        else:
            print(f"\nFound {len(articles)} articles:\n")
            
            # Loop through each article in the list
            for i, article in enumerate(articles):
                # Each 'article' is a dictionary. We want the 'title' and 'url'.
                print(f"--- Article {i + 1} ---")
                print(f"Title: {article['title']}")
                print(f"URL: {article['url']}")
                print("-" * 20) # A separator for readability

    else:
        # If the 'status' is not 'ok', print the error message from the API
        print(f"Error fetching news: {top_headlines.get('message')}")

except Exception as e:
    print(f"An error occurred during the API request: {e}")
    print("This could be due to an invalid API key, network issues, or API rate limits.")