# app/ai_modules/data_processing.py
import re

def clean_data(data: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Remove special characters
            cleaned[key] = re.sub(r'[^\w\s]', '', value).strip()
        else:
            cleaned[key] = value
    return cleaned


# app/ai_modules/data_processing.py
def structure_data(google_data: Dict[str, Any],
                   linkedin_data: Dict[str, Any],
                   yelp_data: Dict[str, Any],
                   website_data: Dict[str, Any]) -> Dict[str, Any]:
    structured = {
        "google_places": google_data,
        "linkedin": linkedin_data,
        "yelp_reviews": yelp_data,
        "website_info": website_data
    }
    return structured


