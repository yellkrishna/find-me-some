# backend/app/ai_modules/data_collection.py

import os
import time
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import logging
from urllib.parse import urljoin, urlparse

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API keys from environment variables
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
YELP_API_KEY = os.getenv("YELP_API_KEY")

def get_google_places_details(business_name, address):
    """
    Retrieve business details from Google Places API.

    Parameters:
        business_name (str): The name of the business.
        address (str): The address of the business.

    Returns:
        dict: A dictionary containing business details.

    Raises:
        ValueError: If no results are found.
        HTTPError: For HTTP request issues.
    """
    logger.info(f"Fetching Google Places details for '{business_name}' at '{address}'")
    search_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": f"{business_name} {address}",
        "inputtype": "textquery",
        "fields": (
            "place_id,name,formatted_address,geometry,types,"
            "website,photos,rating,user_ratings_total,"
            "opening_hours,formatted_phone_number"
        ),
        "key": GOOGLE_PLACES_API_KEY,
    }
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        results = response.json().get("candidates")
        if not results:
            raise ValueError("No results found for the given business name and address.")
        logger.info("Google Places details fetched successfully.")
        return results[0]
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to Google Places API failed: {e}")
        raise

def get_yelp_business_id(business_name, address):
    """
    Retrieve the Yelp business ID for a given business name and address.

    Parameters:
        business_name (str): The name of the business.
        address (str): The address of the business.

    Returns:
        str: The Yelp business ID.

    Raises:
        ValueError: If no business is found.
        HTTPError: For HTTP request issues.
    """
    logger.info(f"Fetching Yelp business ID for '{business_name}' at '{address}'")
    search_url = "https://api.yelp.com/v3/businesses/search"
    headers = {
        "Authorization": f"Bearer {YELP_API_KEY}",
    }
    params = {
        "term": business_name,
        "location": address,
        "limit": 1,
    }
    try:
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        businesses = response.json().get("businesses")
        if not businesses:
            raise ValueError("No Yelp business found for the given name and address.")
        business_id = businesses[0]["id"]
        logger.info(f"Yelp business ID '{business_id}' fetched successfully.")
        return business_id
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to Yelp API failed: {e}")
        raise

def get_yelp_reviews(business_id):
    """
    Retrieve reviews for a Yelp business.

    Parameters:
        business_id (str): The Yelp business ID.

    Returns:
        list: A list of reviews.

    Raises:
        HTTPError: For HTTP request issues.
    """
    logger.info(f"Fetching Yelp reviews for business ID '{business_id}'")
    reviews_url = f"https://api.yelp.com/v3/businesses/{business_id}/reviews"
    headers = {
        "Authorization": f"Bearer {YELP_API_KEY}",
    }
    try:
        response = requests.get(reviews_url, headers=headers)
        response.raise_for_status()
        reviews = response.json().get("reviews", [])
        logger.info("Yelp reviews fetched successfully.")
        return reviews
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to Yelp Reviews API failed: {e}")
        raise

def scrape_company_website(website_url, max_pages=10, max_depth=2):
    """
    Crawl and scrape the company's website content.

    Parameters:
        website_url (str): The URL of the company's website.
        max_pages (int): Maximum number of pages to crawl.
        max_depth (int): Maximum depth to crawl.

    Returns:
        list: A list of dictionaries containing extracted information from each page.

    Raises:
        Exception: For issues during crawling.
    """
    logger.info(f"Crawling company website starting at '{website_url}'")

    # Set up crawling parameters
    visited_urls = set()
    to_visit = [(website_url, 0)]  # Tuple of (url, depth)
    scraped_data = []

    try:
        parsed_url = urlparse(website_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # Start crawling
        while to_visit and len(visited_urls) < max_pages:
            current_url, depth = to_visit.pop(0)
            if current_url in visited_urls or depth > max_depth:
                continue

            try:
                logger.info(f"Scraping URL: {current_url}")
                response = requests.get(current_url)
                response.raise_for_status()
                visited_urls.add(current_url)

                # Parse the HTML content
                soup = BeautifulSoup(response.content, 'lxml')

                # Extract data from the page
                page_data = {
                    'url': current_url,
                    'title': soup.title.string if soup.title else '',
                    'meta_description': '',
                    'headings': {
                        'h1': [],
                        'h2': [],
                        'h3': [],
                    },
                    'content': '',
                }

                # Meta description
                meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
                if meta_desc_tag:
                    page_data['meta_description'] = meta_desc_tag.get('content', '')

                # Headings
                page_data['headings']['h1'] = [h.get_text(strip=True) for h in soup.find_all('h1')]
                page_data['headings']['h2'] = [h.get_text(strip=True) for h in soup.find_all('h2')]
                page_data['headings']['h3'] = [h.get_text(strip=True) for h in soup.find_all('h3')]

                # Paragraphs
                paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
                page_data['content'] = '\n'.join(paragraphs)

                scraped_data.append(page_data)

                # Find new links to follow
                if len(visited_urls) < max_pages and depth < max_depth:
                    for link_tag in soup.find_all('a', href=True):
                        href = link_tag['href']
                        full_url = urljoin(current_url, href)
                        # Stay within the same domain
                        if urlparse(full_url).netloc == parsed_url.netloc:
                            if full_url not in visited_urls:
                                to_visit.append((full_url, depth + 1))

                # Polite crawling: delay between requests
                time.sleep(1)

            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to scrape {current_url}: {e}")
                continue

        logger.info("Website crawling completed successfully.")
        return scraped_data

    except Exception as e:
        logger.error(f"Website crawling failed: {e}")
        raise


def collect_data(business_name, address):
    """
    Collect data from Google Places, Yelp, and the company's website.

    Parameters:
        business_name (str): The name of the business.
        address (str): The address of the business.

    Returns:
        dict: A dictionary containing collected data.

    Raises:
        Exception: Propagates exceptions from called functions.
    """
    try:
        # Google Places Data
        google_data = get_google_places_details(business_name, address)
        
        # Yelp Data
        yelp_business_id = get_yelp_business_id(business_name, address)
        yelp_reviews = get_yelp_reviews(yelp_business_id)
        
        # Company Website Data
        website_url = google_data.get("website")
        if website_url:
            website_content = scrape_company_website(website_url)
        else:
            website_content = None
            logger.info("Website URL not available from Google Places data.")
        
        # Combine collected data
        collected_data = {
            "google_places": google_data,
            "yelp_reviews": yelp_reviews,
            "website_content": website_content,
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


