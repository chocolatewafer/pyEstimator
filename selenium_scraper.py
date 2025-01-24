from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time, re


def get_product_details(link):
    """
    Fetches product name and price from a product page using Selenium.
    """
    # Set up Selenium options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU (not recommended for hardware acceleration)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--enable-unsafe-swiftshader")  # Enable SwiftShader with lower security guarantees
    chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors
    chrome_options.add_argument("--disable-dev-shm-usage")  # Disable shared memory usage (suppresses USB errors)

    # Set up WebDriver using webdriver_manager
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(link)
        # Wait for the page to load (adjust sleep time as needed)
        time.sleep(5)

        # Extract product name
        product_name = driver.find_element(By.TAG_NAME, "h1").text

        # Extract price
        # Try multiple possible class combinations for the price
        price = None
        price_selectors = [
            ".pdp-product-price .pdp-price",  # Example: <div class="pdp-product-price"><span class="pdp-price">Rs. 1,290</span></div>
            ".pdp-price",  # Fallback: Directly look for elements with class "pdp-price"
            ".price",  # Fallback: Look for elements with class "price"
            ".product-price",  # Fallback: Look for elements with class "product-price"
        ]

        for selector in price_selectors:
            try:
                price_element = driver.find_element(By.CSS_SELECTOR, selector)
                price_text = price_element.text
                # Extract numeric value from the price text
                price_match = re.search(r"Rs\.?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", price_text)
                if price_match:
                    price = float(price_match.group(1).replace(",", ""))
                    break
            except Exception as e:
                continue  # If the selector fails, try the next one

        if not price:
            raise ValueError("Price not found on the page")

        return product_name, price

    except Exception as e:
        raise ValueError(f"Failed to scrape product details: {e}")
    finally:
        driver.quit()