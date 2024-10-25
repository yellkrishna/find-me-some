# app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .ai_modules.data_collection.data_collection import collect_data
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

class WebsiteInfo(BaseModel):
    website_url: str

@app.post("/collect-data/")
async def collect_website_data(info: WebsiteInfo):
    try:
        # Step 1: Data Collection
        collected_data = collect_data(info.website_url)

        # Commenting out the rest of the steps for now
        # Step 2: Data Cleaning
        # Step 3: Data Structuring
        # Step 4: Data Enrichment
        # Step 5: Indexing
        # Step 6: Summarization

        # Step 7: Store in Supabase
        data_to_store = {
            "website_url": info.website_url,
            "website_data": collected_data.get("website_data"),
        }
        supabase.table("website_data").insert(data_to_store).execute()

        return {"message": "Data collected and stored successfully.", "data": data_to_store}

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
