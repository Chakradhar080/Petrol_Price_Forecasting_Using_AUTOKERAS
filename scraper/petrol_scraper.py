"""
Web scraper for Indian petrol prices.
Supports multiple sources with fallback mechanisms.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import setup_logger

logger = setup_logger(__name__, 'logs/scraper.log')

class PetrolPriceScraper:
    """Scraper for Indian petrol prices from various sources"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_goodreturns(self, city='delhi'):
        """
        Scrape petrol prices from GoodReturns.in
        
        Args:
            city: City name (default: delhi)
        
        Returns:
            dict: {date: datetime, price: float, source: str}
        """
        try:
            url = f'https://www.goodreturns.in/petrol-price-in-{city}.html'
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find price element (structure may vary, adjust selectors as needed)
            price_element = soup.find('td', {'id': 'todays_price'})
            if not price_element:
                # Try alternative selector
                price_element = soup.find('span', class_='price_value')
            
            if price_element:
                price_text = price_element.text.strip()
                # Extract numeric value (e.g., "₹ 96.72" -> 96.72)
                price = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_text)))
                
                return {
                    'date': datetime.now().date(),
                    'price': price,
                    'source': 'goodreturns'
                }
            else:
                logger.warning("Could not find price element on GoodReturns")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping GoodReturns: {str(e)}")
            return None
    
    def scrape_with_selenium(self, url, price_selector):
        """
        Fallback scraper using Selenium for JavaScript-heavy sites
        
        Args:
            url: Target URL
            price_selector: CSS selector for price element
        
        Returns:
            dict: {date: datetime, price: float, source: str}
        """
        driver = None
        try:
            # Set up headless Chrome
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            # Wait for price element to load
            wait = WebDriverWait(driver, 10)
            price_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, price_selector))
            )
            
            price_text = price_element.text.strip()
            price = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_text)))
            
            return {
                'date': datetime.now().date(),
                'price': price,
                'source': 'selenium_scraper'
            }
            
        except Exception as e:
            logger.error(f"Error with Selenium scraper: {str(e)}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def get_latest_price(self, city='delhi'):
        """
        Get latest petrol price with fallback mechanisms
        
        Args:
            city: City name
        
        Returns:
            dict: {date: datetime, price: float, source: str} or None
        """
        # Try primary source
        result = self.scrape_goodreturns(city)
        
        if result:
            logger.info(f"Successfully scraped petrol price: ₹{result['price']} on {result['date']}")
            return result
        
        # Add more fallback sources here if needed
        logger.warning("All scraping methods failed")
        return None
    
    def get_historical_prices(self, start_date, end_date, city='delhi'):
        """
        Get historical petrol prices (if available from source)
        Note: Most free sources don't provide historical data via scraping
        
        Args:
            start_date: Start date
            end_date: End date
            city: City name
        
        Returns:
            list: List of {date, price, source} dicts
        """
        logger.warning("Historical scraping not implemented - use file upload for historical data")
        return []

# Convenience function
def fetch_petrol_price(city='delhi'):
    """Fetch latest petrol price"""
    scraper = PetrolPriceScraper()
    return scraper.get_latest_price(city)
