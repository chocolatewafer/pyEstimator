from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import re
import time


def search_product(product_name):
    """
    Searches for a product on Google, Bing, and DuckDuckGo and returns the price and URL from the first result where the price is found.
    """
    # Set up Selenium options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU (not recommended for hardware acceleration)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--enable-unsafe-swiftshader")  # Enable SwiftShader with lower security guarantees
    chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors
    chrome_options.add_argument("--disable-dev-shm-usage")  # Disable shared memory usage (suppresses USB errors)
    chrome_options.add_argument("--log-level=3")  # Suppress logs

    # Set up WebDriver using webdriver_manager
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # List of search engines to try
        search_engines = [
            ("Google", "https://www.google.com", "q"),
            ("Bing", "https://www.bing.com", "q"),
            ("DuckDuckGo", "https://duckduckgo.com", "q")
        ]

        for engine_name, url, search_box_name in search_engines:
            try:
                # Open the search engine
                driver.get(url)

                # Search for the product
                search_box = driver.find_element(By.NAME, search_box_name)
                search_box.send_keys(f"{product_name} price in Nepal")
                search_box.send_keys(Keys.RETURN)

                # Wait for the search results to load
                time.sleep(5)

                # Get the top 5 results
                if engine_name == "Google":
                    results = driver.find_elements(By.CSS_SELECTOR, ".tF2Cxc")[:5]
                elif engine_name == "Bing":
                    results = driver.find_elements(By.CSS_SELECTOR, ".b_algo")[:5]
                elif engine_name == "DuckDuckGo":
                    results = driver.find_elements(By.CSS_SELECTOR, ".result")[:5]

                # Parse the price from the results
                for result in results:
                    if engine_name == "Google":
                        description = result.find_element(By.CSS_SELECTOR, ".IsZvec").text
                        link = result.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    elif engine_name == "Bing":
                        description = result.find_element(By.CSS_SELECTOR, ".b_caption p").text
                        link = result.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    elif engine_name == "DuckDuckGo":
                        description = result.find_element(By.CSS_SELECTOR, ".result__snippet").text
                        link = result.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

                    # Search for the price in the description
                    price_match = re.search(r"NRs\.?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", description)
                    if price_match:
                        price = float(price_match.group(1).replace(",", ""))
                        return price, link

            except Exception as e:
                print(f"Error searching on {engine_name}: {e}")
                continue

        # If no price is found
        return None, None

    finally:
        driver.quit()