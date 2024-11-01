# app/ai_modules/data_enrichment/enrichment.py

import os
import requests
import logging
from typing import Dict, Any, Optional
from time import sleep
from requests.exceptions import HTTPError, RequestException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Adjust as needed
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)

def get_google_places_details(
    business_name: str,
    address: str,
    retries: int = 3,
    backoff_factor: float = 0.3
) -> Optional[Dict[str, Any]]:
    """
    Retrieve business details from Google Places API.

    Parameters:
        business_name (str): The name of the business.
        address (str): The address of the business.
        retries (int): Number of retry attempts for transient errors.
        backoff_factor (float): Factor by which the delay increases between retries.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing business details if found, else None.

    Raises:
        ValueError: If no results are found.
        HTTPError: For HTTP request issues.
    """
    logger.info(f"Fetching Google Places details for '{business_name}' at '{address}'")

    # Fetch API key from environment variables
    google_places_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not google_places_api_key:
        logger.error("GOOGLE_PLACES_API_KEY is not set in environment variables.")
        raise EnvironmentError("GOOGLE_PLACES_API_KEY is not set in environment variables.")

    search_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": f"{business_name} {address}",
        "inputtype": "textquery",
        "fields": (
            "place_id,name,formatted_address,geometry,types,"
            "website,photos,rating,user_ratings_total,"
            "opening_hours,formatted_phone_number"
        ),
        "key": google_places_api_key,
    }

    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            data = response.json()
            results = data.get("candidates", [])

            if not results:
                logger.warning(f"No results found for '{business_name}' at '{address}'.")
                raise ValueError("No results found for the given business name and address.")

            logger.info(f"Google Places details fetched successfully for '{business_name}'.")
            return results[0]

        except HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err} - Response: {response.text}")
            # Do not retry for client-side errors (4xx)
            if 400 <= response.status_code < 500:
                raise
            attempt += 1
            sleep(backoff_factor * (2 ** (attempt - 1)))  # Exponential backoff
            logger.info(f"Retrying... Attempt {attempt}/{retries}")

        except RequestException as req_err:
            logger.error(f"Request exception occurred: {req_err}")
            attempt += 1
            sleep(backoff_factor * (2 ** (attempt - 1)))
            logger.info(f"Retrying... Attempt {attempt}/{retries}")

        except ValueError as val_err:
            logger.error(val_err)
            raise

    logger.error(f"Failed to fetch Google Places details for '{business_name}' after {retries} attempts.")
    return None
