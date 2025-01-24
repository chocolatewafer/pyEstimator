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
    Searches for a product on Google and returns the price and URL from the first result where the price is found.
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
        # Open Google
        driver.get("https://www.google.com")

        # Search for the product
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(f"{product_name} price in Nepal")
        search_box.send_keys(Keys.RETURN)

        # Wait for the search results to load
        time.sleep(5)

        # Get the top 3 results
        results = driver.find_elements(By.CSS_SELECTOR, ".tF2Cxc")[:3]

        # Parse the price from the results
        for result in results:
            description = result.find_element(By.CSS_SELECTOR, ".IsZvec").text
            price_match = re.search(r"NRs\.?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", description)
            if price_match:
                price = float(price_match.group(1).replace(",", ""))
                link = result.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                return price, link

        # If no price is found
        return None, None
    except Exception as e:
        print(f"Error searching for product: {e}")
        return None, None
    finally:
        driver.quit()