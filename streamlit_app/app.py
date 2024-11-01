# streamlit_app/app.py

import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# FastAPI backend URL (ensure this matches where your FastAPI app is running)
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

# Initialize session state for dom_content
if 'dom_content' not in st.session_state:
    st.session_state.dom_content = []

st.set_page_config(page_title="Find-Me-Some", layout="wide")
st.title("Find-Me-Some: Website Data Collection")

st.sidebar.header("Input Parameters")

# User input for website URL
website_url = st.sidebar.text_input("Enter the Website URL:", "https://www.example.com/")

# Button to trigger data collection
if st.sidebar.button("Collect Data"):
    with st.spinner("Collecting data..."):
        try:
            # Send POST request to FastAPI endpoint
            response = requests.post(
                f"{FASTAPI_URL}/collect-data/",
                json={"website_url": website_url}
            )
            if response.status_code == 200:
                st.success("Data collected and stored successfully!")
                data = response.json().get("data")
                st.subheader("Collected Data")
                st.json(data)
                
                # Extract and store split content
                dom_content = []
                website_data = data.get("website_data", [])
                for page in website_data:
                    url = page.get("url", "N/A")
                    chunks = page.get("content_chunks", [])
                    for idx, chunk in enumerate(chunks, 1):
                        dom_content.append({
                            "page_url": url,
                            "chunk_number": idx,
                            "content": chunk
                        })
                
                st.session_state.dom_content = dom_content
                st.success("DOM content split into chunks and stored in session state.")
            else:
                error_detail = response.json().get("detail", "Unknown error occurred.")
                st.error(f"Error: {error_detail}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Fetch and display existing data
st.sidebar.markdown("---")
st.sidebar.header("Retrieve Existing Data")

# Input for retrieving existing data
retrieve_url = st.sidebar.text_input("Enter Website URL to Retrieve Data:", "")

if st.sidebar.button("Retrieve Data"):
    if retrieve_url:
        with st.spinner("Retrieving data..."):
            try:
                # Send GET request to FastAPI endpoint
                response = requests.get(
                    f"{FASTAPI_URL}/get-website-data/",
                    params={"website_url": retrieve_url}
                )
                if response.status_code == 200:
                    data = response.json().get("data")
                    st.subheader("Retrieved Data")
                    st.json(data)
                    
                    # Extract and store split content
                    dom_content = []
                    website_data = data.get("website_data", [])
                    for page in website_data:
                        url = page.get("url", "N/A")
                        chunks = page.get("content_chunks", [])
                        for idx, chunk in enumerate(chunks, 1):
                            dom_content.append({
                                "page_url": url,
                                "chunk_number": idx,
                                "content": chunk
                            })
                    
                    st.session_state.dom_content = dom_content
                    st.success("DOM content retrieved and stored in session state.")
                else:
                    error_detail = response.json().get("detail", "Data not found.")
                    st.error(f"Error: {error_detail}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a website URL to retrieve data.")

# Display Split DOM Content
st.header("Split DOM Content")

if st.session_state.dom_content:
    # Organize content by page URL
    pages = {}
    for chunk in st.session_state.dom_content:
        url = chunk['page_url']
        if url not in pages:
            pages[url] = []
        pages[url].append(chunk)
    
    # Create tabs for each page
    tabs = st.tabs(list(pages.keys()))
    
    for tab, url in zip(tabs, pages.keys()):
        with tab:
            st.subheader(f"Page: {url}")
            for chunk in pages[url]:
                with st.expander(f"Chunk {chunk['chunk_number']}"):
                    st.markdown(chunk['content'])
                st.markdown("---")  # Divider between chunks
else:
    st.info("No DOM content to display. Please collect data first.")
