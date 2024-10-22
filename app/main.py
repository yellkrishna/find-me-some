# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ai_modules.data_collection import get_google_places_details, scrape_linkedin_company, get_yelp_reviews, scrape_company_website
from ai_modules.data_processing import clean_data, structure_data
from ai_modules.data_enrichment import geocode_address, classify_industry
from ai_modules.summarization import index_data, generate_business_summary
from ai_modules.utils import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

app = FastAPI()

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class BusinessInfo(BaseModel):
    name: str
    address: str

@app.post("/generate-summary/")
async def generate_summary(info: BusinessInfo):
    try:
        # Step 1: Data Collection
        google_data = get_google_places_details(info.name, info.address)
        linkedin_data = scrape_linkedin_company(info.name, info.address)
        yelp_data = get_yelp_reviews(info.name, info.address)
        website_url = google_data.get("website", "")
        website_data = scrape_company_website(website_url) if website_url else {}
        
        # Step 2: Data Cleaning
        cleaned_google = clean_data(google_data)
        cleaned_linkedin = clean_data(linkedin_data)
        cleaned_yelp = clean_data(yelp_data)
        cleaned_website = clean_data(website_data)
        
        # Step 3: Data Structuring
        structured = structure_data(cleaned_google, cleaned_linkedin, cleaned_yelp, cleaned_website)
        
        # Step 4: Data Enrichment
        geocoded = geocode_address(info.address)
        structured['geocoding'] = geocoded
        industry = classify_industry(google_data.get("types", [""])[0])  # Assuming first type represents industry
        structured['industry'] = industry
        
        # Step 5: Indexing
        index = index_data(structured)
        
        # Step 6: Summarization
        summary = generate_business_summary(index)
        
        # Step 7: Store in Supabase
        data_to_store = {
            "name": info.name,
            "address": info.address,
            "summary": summary,
            "geocoded_address": geocoded,
            "industry": industry
        }
        supabase.table("business_summaries").insert(data_to_store).execute()
        
        return {"summary": summary}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
