import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import re
import time

# API keys for search engines (replace with your own keys)
BING_API_KEY = "YOUR_BING_API_KEY"
SERPAPI_KEY = "67e4610fe960a5b78895ca120b6e88edd350d2a3"

def search_with_bing_api(query):
    """
    Searches for a product using the Bing Search API.
    """
    try:
        url = f"https://api.bing.microsoft.com/v7.0/search?q={query}"
        headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if "webPages" in data and "value" in data["webPages"]:
            for result in data["webPages"]["value"]:
                link = result.get("url", "")
                snippet = result.get("snippet", "")
                if "NPR" in snippet or "Rs." in snippet:
                    price = extract_price_from_text(snippet)
                    if price:
                        return price, link
        return None, None
    except Exception as e:
        print(f"Error searching with Bing API: {e}")
        return None, None

def search_with_serpapi(query):
    """
    Searches for a product using SerpAPI (for Google).
    """
    try:
        url = f"https://google.serper.dev/search.json?q={query}&api_key={SERPAPI_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "organic_results" in data:
            for result in data["organic_results"]:
                link = result.get("link", "")
                snippet = result.get("snippet", "")
                if "NPR" in snippet or "Rs." in snippet:
                    price = extract_price_from_text(snippet)
                    if price:
                        return price, link
        return None, None
    except Exception as e:
        print(f"Error searching with SerpAPI: {e}")
        return None, None

def extract_price_from_text(text):
    """
    Extracts the price from a text snippet.
    """
    price_match = re.search(r"Rs\.?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", text)
    if price_match:
        return float(price_match.group(1).replace(",", ""))
    return None

def search_with_selenium(product_name, search_engine, url, search_box_name, result_selector):
    """
    Searches for a product using Selenium on a given search engine.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")

    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        search_box = driver.find_element(By.NAME, search_box_name)
        search_box.send_keys(f"{product_name} price in Nepal Daraz")
        search_box.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, result_selector))
        )

        results = driver.find_elements(By.CSS_SELECTOR, result_selector)[:5]
        for result in results:
            try:
                link = result.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                snippet = result.text
                if "NPR" in snippet or "Rs." in snippet:
                    price = extract_price_from_text(snippet)
                    if price:
                        return price, link
            except Exception as e:
                print(f"Error extracting metadata from result: {e}")
                continue
        return None, None
    except Exception as e:
        print(f"Error searching on {search_engine}: {e}")
        return None, None
    finally:
        driver.quit()

def search_product(product_name):
    """
    Searches for a product using multiple search engines and APIs.
    """
    # Try Bing API first
    price, link = search_with_bing_api(f"{product_name} price in Nepal Daraz")
    if price:
        return price, link

    # Try SerpAPI (Google) next
    price, link = search_with_serpapi(f"{product_name} price in Nepal Daraz")
    if price:
        return price, link

    # Fallback to Selenium-based search engines
    search_engines = [
        ("Bing", "https://www.bing.com", "q", ".b_algo"),
        ("Google", "https://www.google.com", "q", ".tF2Cxc"),
        ("DuckDuckGo", "https://duckduckgo.com", "q", ".result"),
        ("Yahoo", "https://search.yahoo.com", "p", ".algo"),
        ("Ecosia", "https://www.ecosia.org", "q", ".result"),
    ]

    for engine_name, url, search_box_name, result_selector in search_engines:
        price, link = search_with_selenium(product_name, engine_name, url, search_box_name, result_selector)
        if price:
            return price, link

    # If no price is found
    return None, None