# app/ai_modules/data_collection/scrape.py

import time
import logging
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

def scrape_company_website(website_url, max_pages=10, max_depth=2):
    logger.info(f"Crawling company website starting at '{website_url}'")

    visited_urls = set()
    to_visit = [(website_url, 0)]  # Tuple of (url, depth)
    scraped_data = []

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("--log-level=3")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except WebDriverException as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        raise

    try:
        parsed_url = urlparse(website_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        while to_visit and len(visited_urls) < max_pages:
            current_url, depth = to_visit.pop(0)
            normalized_url = current_url.rstrip('/')
            if normalized_url in visited_urls or depth > max_depth:
                continue

            try:
                logger.info(f"Scraping URL: {current_url}")
                driver.get(current_url)
                time.sleep(2)  # Wait for JavaScript to load content

                visited_urls.add(normalized_url)
                html = driver.page_source

                try:
                    # Use readability to extract the main content
                    doc = Document(html)
                    content_html = doc.summary()
                    soup = BeautifulSoup(content_html, 'lxml')
                    text = soup.get_text(separator='\n').strip()

                    if not text:
                        logger.warning(f"Readability failed to extract content from {current_url}, falling back to full page text.")
                        # Fallback: if readability doesn't return content, use BeautifulSoup directly
                        soup = BeautifulSoup(html, 'lxml')
                        text = soup.get_text(separator='\n').strip()
                
                except Exception as e:
                    logger.error(f"Error using readability on {current_url}: {e}")
                    # Fallback: process full HTML text if readability fails
                    soup = BeautifulSoup(html, 'lxml')
                    text = soup.get_text(separator='\n').strip()

                # Clean up the text
                lines = [line.strip() for line in text.splitlines()]
                text = '\n'.join(line for line in lines if line)
                text = re.sub(r'\n\s*\n', '\n\n', text)  # Remove multiple blank lines

                # Extract data from the page
                page_data = {
                    'url': current_url,
                    'title': doc.title() if 'doc' in locals() else soup.title.string.strip() if soup.title else '',
                    'meta_description': '',
                    'headings': {
                        'h1': [h.get_text(strip=True) for h in soup.find_all('h1')],
                        'h2': [h.get_text(strip=True) for h in soup.find_all('h2')],
                        'h3': [h.get_text(strip=True) for h in soup.find_all('h3')],
                    },
                    'content': text,  # Cleaned plain text content
                }

                # Meta description
                meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
                if meta_desc_tag:
                    page_data['meta_description'] = meta_desc_tag.get('content', '').strip()

                scraped_data.append(page_data)
                logger.info(f"Scraped content from {current_url}")

                # Find new links to follow
                if len(visited_urls) < max_pages and depth < max_depth:
                    for link_tag in soup.find_all('a', href=True):
                        href = link_tag['href']
                        full_url = urljoin(current_url, href)
                        full_url = full_url.split('#')[0].rstrip('/')  # Normalize URL
                        if urlparse(full_url).netloc == parsed_url.netloc:
                            if full_url not in visited_urls:
                                to_visit.append((full_url, depth + 1))

                time.sleep(1)

            except Exception as e:
                logger.error(f"Failed to scrape {current_url}: {e}")
                continue

        logger.info("Website crawling completed successfully.")
        return scraped_data

    except Exception as e:
        logger.error(f"Website crawling failed: {e}")
        raise
    finally:
        driver.quit()

