# app/ai_modules/data_collection.py
import requests
from typing import Dict, Any
from .utils import GOOGLE_PLACES_API_KEY

def get_google_places_details(business_name: str, address: str) -> Dict[str, Any]:
    search_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": f"{business_name} {address}",
        "inputtype": "textquery",
        "fields": "place_id,name,formatted_address,geometry,types,website,photos",
        "key": GOOGLE_PLACES_API_KEY
    }
    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        raise Exception(f"Google Places API Error: {response.text}")
    results = response.json().get("candidates")
    if not results:
        raise Exception("No results found for the given business name and address.")
    return results[0]

# app/ai_modules/data_collection.py
from bs4 import BeautifulSoup
import requests

def scrape_linkedin_company(business_name: str, address: str) -> Dict[str, Any]:
    search_query = f"{business_name} {address}"
    search_url = f"https://www.linkedin.com/search/results/all/?keywords={requests.utils.quote(search_query)}"
    headers = {
        "User-Agent": "Your User Agent String"
    }
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"LinkedIn Scraping Error: {response.text}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    # Parsing logic goes here based on LinkedIn's HTML structure
    # This is subject to change and may require frequent updates
    company_data = {}
    # Example extraction (pseudo-code)
    # company_data['name'] = soup.find(...).text
    # company_data['employees'] = soup.find(...).text
    return company_data


# app/ai_modules/data_collection.py
def get_yelp_reviews(business_name: str, address: str) -> Dict[str, Any]:
    yelp_api_key = os.getenv("YELP_API_KEY")
    search_url = "https://api.yelp.com/v3/businesses/search"
    headers = {
        "Authorization": f"Bearer {yelp_api_key}"
    }
    params = {
        "term": business_name,
        "location": address,
        "limit": 1
    }
    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Yelp API Error: {response.text}")
    businesses = response.json().get("businesses")
    if not businesses:
        raise Exception("No Yelp reviews found for the given business.")
    business_id = businesses[0]['id']
    
    reviews_url = f"https://api.yelp.com/v3/businesses/{business_id}/reviews"
    reviews_response = requests.get(reviews_url, headers=headers)
    if reviews_response.status_code != 200:
        raise Exception(f"Yelp Reviews API Error: {reviews_response.text}")
    return reviews_response.json()

# app/ai_modules/data_collection.py
def scrape_company_website(website_url: str) -> Dict[str, Any]:
    headers = {
        "User-Agent": "Your User Agent String"
    }
    response = requests.get(website_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Website Scraping Error: {response.text}")
    soup = BeautifulSoup(response.text, 'html.parser')
    # Extract relevant information
    company_info = {}
    # Example extraction (pseudo-code)
    # company_info['description'] = soup.find('meta', {'name': 'description'})['content']
    return company_info
