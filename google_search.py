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

def search_product(product_name):
    """
    Searches for a product on Google, Bing, and DuckDuckGo and returns the price and URL from the top result.
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
            ("Google", "https://www.google.com", "q", ".tF2Cxc"),  # Google result container
            ("Bing", "https://www.bing.com", "q", ".b_algo"),  # Bing result container
            ("DuckDuckGo", "https://duckduckgo.com", "q", ".result")  # DuckDuckGo result container
        ]

        for engine_name, url, search_box_name, result_selector in search_engines:
            try:
                # Open the search engine
                driver.get(url)

                # Search for the product with "price in Nepal Daraz"
                search_box = driver.find_element(By.NAME, search_box_name)
                search_box.send_keys(f"{product_name} price in Nepal Daraz")
                search_box.send_keys(Keys.RETURN)

                # Wait for the search results to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, result_selector))
                )

                # Get the top result link
                top_result = driver.find_element(By.CSS_SELECTOR, result_selector)
                link = top_result.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

                # Print the top result link
                print(f"Search Engine: {engine_name}")
                print(f"Top Result Link: {link}")

                # Send the link to selenium_scraper.py to extract the price
                from selenium_scraper import get_product_details
                try:
                    product_name, price = get_product_details(link)
                    if price:
                        return price, link
                except Exception as e:
                    print(f"Error extracting price from {link}: {e}")
                    continue

            except Exception as e:
                print(f"Error searching on {engine_name}: {e}")
                continue

        # If no price is found
        return None, None

    finally:
        driver.quit()