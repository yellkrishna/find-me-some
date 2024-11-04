# backend/app/ai_modules/data_collection.py

import os
from time import sleep
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import logging
from urllib.parse import urljoin, urlparse
from .scrape import scrape_company_website
from typing import Dict, Any, Optional
from requests.exceptions import HTTPError, RequestException
from ..text_splitter import split_text

from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS 

load_dotenv()

# Configure logging
logging.basicConfig(
    filename='app.log',  # Set the log file name
    level=logging.INFO,  # Set the log level
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)
logger = logging.getLogger(__name__)

# Load API keys from environment variables
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
# YELP_API_KEY = os.getenv("YELP_API_KEY")

def collect_data(website_url):
    """
    Collect data by scraping the company's website, splitting content into chunks,
    and computing embeddings.

    Parameters:
        website_url (str): The URL of the company's website.

    Returns:
        dict: A dictionary containing collected website data and vector store.
    """
    try:
        # Step 1: Data Collection
        if website_url:
            website_data = scrape_company_website(website_url)
        else:
            website_data = None
            logger.info("Website URL not provided.")

        # Step 2: Split the content into chunks and create Documents
        documents = []
        if website_data:
            for page in website_data:
                content = page.get('content', '')
                chunks = split_text(content)
                page['content_chunks'] = chunks  # Add chunks to the page data

                # Create Document objects for each chunk
                for idx, chunk in enumerate(chunks):
                    doc = Document(
                        page_content=chunk,
                        metadata={
                            'page_url': page.get('url', ''),
                            'chunk_number': idx + 1,
                            'title': page.get('title', ''),
                            'meta_description': page.get('meta_description', ''),
                            'headings': page.get('headings', {})
                        }
                    )
                    documents.append(doc)
        else:
            logger.info("No website data to split.")

        # Step 3: Compute Embeddings and Create Vector Store
        if documents:
            OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            if not OPENAI_API_KEY:
                logger.error("OPENAI_API_KEY is not set in the environment variables.")
                raise ValueError("OpenAI API key not found.")
            
            embedding_function = OpenAIEmbeddings(
                model="text-embedding-ada-002",  # Specify the model explicitly
                openai_api_key=OPENAI_API_KEY
            )
            vector_store = FAISS.from_documents(documents, embedding_function)
            logger.info("Embeddings computed and vector store created.")
        else:
            vector_store = None
            logger.info("No documents to compute embeddings.")

        # Combine collected data
        collected_data = {
            "website_data": website_data,
            "vector_store": vector_store
        }
        logger.info("Data collection completed successfully.")
        return collected_data
    except Exception as e:
        logger.error(f"Data collection failed: {e}")
        raise


# Remove after testing. Check correct functionality in main.py. 
if __name__ == "__main__":
    website_url = "https://www.apfmteam.com/"
    try:
        # Set desired max_pages and max_depth
        max_pages = 10
        max_depth = 2

        # Call the scrape_company_website function
        website_data = scrape_company_website(website_url, max_pages=max_pages, max_depth=max_depth)

        # Print the collected data
        print("Website Data:")
        for page in website_data:
            print(f"Page URL: {page['url']}")
            print(f"Title: {page['title']}")
            print(f"Meta Description: {page['meta_description']}")
            print(f"H1 Headings: {page['headings']['h1']}")
            print(f"Content Snippet: {page['content'][:200]}...")  # Display first 200 characters
            print("-" * 80)
    except Exception as e:
        print("An error occurred during website crawling:", e)


