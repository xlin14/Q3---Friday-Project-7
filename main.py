# Import the client libraries
from newsapi import NewsApiClient
import openai
import os # Added for handling API keys securely
from dotenv import load_dotenv # Import dotenv
import requests # For fetching article content from URLs
from bs4 import BeautifulSoup # For parsing the article HTML

# --- STEP 1: SETUP ---

# Load API keys from .env files
# Make sure to install the libraries:
# pip install python-dotenv newsapi-python openai requests beautifulsoup4

# This loads the .env file from the same directory as this script
# The .env file should look like this:
#
# NEWS_API_KEY='your_key_from_newsapi_org'
# OPENAI_API_KEY='sk-your_key_from_openai'
#
load_dotenv()


# --- NewsAPI Setup ---
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

# --- OpenAI Setup ---
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


# --- NEW: Check for API Keys ---
# This check runs before we try to use the keys.
if not NEWS_API_KEY:
    print("--- ERROR: NEWS_API_KEY not found ---")
    print("Please create a file named '.env' in the same folder as main.py.")
    print("Add this line to the .env file:")
    print("NEWS_API_KEY='your_actual_key_from_newsapi_org'")
    print("-" * 40)
    exit()

if not OPENAI_API_KEY:
    print("--- ERROR: OPENAI_API_KEY not found ---")
    print("Please check your '.env' file.")
    print("Add this line to the .env file:")
    print("OPENAI_API_KEY='sk-your_actual_key_from_openai'")
    print("-" * 40)
    exit()