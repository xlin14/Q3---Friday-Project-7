# Q3---Friday-Project-7
## AI-Powered Monthly News Newsletter Generator

This Python script automates the entire process of creating and sending a professional, monthly technology newsletter. It fetches the most popular tech articles from the past 30 days, uses an AI to summarize each one, formats them into a clean HTML email, and sends it to a specified recipient.

### How It Works: The Workflow

The script runs in a single, automated sequence, broken down into these main steps:

**1. Setup and Initialization**

Loads Configuration: The script begins by loading all necessary credentials and settings from a single .env file using python-dotenv. This keeps your sensitive API keys and passwords separate from the code. It loads:

NEWS_API_KEY (from NewsAPI.org)

OPENAI_API_KEY (from OpenAI)

SENDER_EMAIL & SENDER_APP_PASSWORD (your Gmail credentials)

RECIPIENT_EMAIL (where to send the newsletter)

NEWS_QUERY (the topics to search for)

Initializes Clients: It securely initializes the NewsAPI and OpenAI clients with your keys, performing a test call to the OpenAI API to ensure the key is valid before proceeding.

**2. Fetching the News**

The script uses the NewsAPI's /v2/everything endpoint to find the most popular articles related to your NEWS_QUERY from the last 30 days.

It sorts these articles by "popularity" and retrieves the top 8 (or as specified by page_size) to ensure the newsletter contains high-impact stories.

**3. Scraping and Summarizing**

For each article retrieved, the script performs a two-step process:

Scraping: It uses the requests and BeautifulSoup4 libraries to fetch the article's webpage and parse the HTML, extracting all paragraph (<p>) text to get the full content. This step includes a "User-Agent" header to mimic a real browser and has error handling for sites that block scraping or are built dynamically.

Summarizing: The full article text is sent to OpenAI's gpt-3.5-turbo model. The AI has been given a system prompt to act as a newsletter assistant and return a single, concise summary paragraph for each article.

**4. Formatting the Newsletter**

As the summaries are generated, the script builds two versions of the newsletter simultaneously:

Plain Text: A simple, clean version for email clients that don't support HTML.

Professional HTML: A fully-styled HTML document with inline CSS for a professional look. This version includes a main header, a subheader with the current month, and cleanly formatted article sections with titles, summaries, and "Read Full Article" links.

**5. Sending the Email**

Once all articles are processed, the script uses Python's built-in smtplib and ssl libraries to send the final email.

It sends a multipart email, providing the HTML version as the main content and the plain-text version as a fallback.

SSL Fix: The script uses ssl._create_unverified_context() to bypass SSL certificate verification. This is a necessary fix for users on networks (like at a school or business) or with antivirus software that intercepts internet traffic, which would otherwise cause the connection to Gmail's server to fail.

## How to Use This Script

Install Libraries:

pip install python-dotenv newsapi-python openai requests beautifulsoup4


Create .env File:
In the same directory as main.py, create a file named .env and add your credentials:

NEWS_API_KEY='your-news-api-key'
OPENAI_API_KEY='your-openai-sk-key'
SENDER_EMAIL='your-email@gmail.com'
SENDER_APP_PASSWORD='your-16-digit-google-app-password'
RECIPIENT_EMAIL='email-to-send-to@example.com'
NEWS_QUERY='(technology OR AI OR programming)'


Note: SENDER_APP_PASSWORD must be a 16-digit "App Password" generated from your Google Account's security settings.

**Run Manually:**

You can run the script at any time to send the newsletter manually:

python main.py


Automate (Optional):
To make this run automatically on the 1st of every month, use your operating system's scheduler (like Task Scheduler on Windows or cron on macOS/Linux) to run the python main.py command.