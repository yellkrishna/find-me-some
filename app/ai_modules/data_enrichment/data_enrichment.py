# app/ai_modules/data_enrichment.py
import requests

def geocode_address(address: str) -> Dict[str, Any]:
    geocoding_api_key = os.getenv("GOOGLE_GEOCODING_API_KEY")
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": geocoding_api_key
    }
    response = requests.get(geocode_url, params=params)
    if response.status_code != 200:
        raise Exception(f"Geocoding API Error: {response.text}")
    results = response.json().get("results")
    if not results:
        raise Exception("No geocoding results found.")
    return results[0]

def classify_industry(business_type: str) -> str:
    # Simple classification logic or use a dedicated API/service
    industry_map = {
        "restaurant": "Food & Beverage",
        "tech": "Technology",
        # Add more mappings as needed
    }
    return industry_map.get(business_type.lower(), "Other")
