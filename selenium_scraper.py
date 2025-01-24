from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def get_product_details(link):
    """
    Fetches product name and price from a Daraz product page using Selenium.
    """
    # Set up Selenium options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Set up WebDriver (update the path to your chromedriver)
    service = Service(executable_path="/path/to/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(link)
        # Wait for the page to load (adjust sleep time as needed)
        import time
        time.sleep(10)

        # Extract product name
        product_name = driver.find_element(By.TAG_NAME, "h1").text

        # Extract price
        price_element = driver.find_element(By.CLASS_NAME, "pdp-price")
        price_text = price_element.text.replace("Rs.", "").replace(",", "").strip()
        price = float(price_text)

        return product_name, price
    except Exception as e:
        raise ValueError(f"Failed to scrape product details: {e}")
    finally:
        driver.quit()