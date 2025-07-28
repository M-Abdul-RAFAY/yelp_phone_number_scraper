import csv
import time
import random
import re
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_driver():
    """Initialize Chrome WebDriver with anti-detection settings"""
    chrome_options = Options()
    # Run in headful mode for debugging
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    # Execute script to remove webdriver property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def search_yelp_businesses(driver, category, location, max_pages=3):
    """Search Yelp for businesses based on category and location"""
    business_urls = []
    
    try:
        # Construct search URL
        encoded_category = urllib.parse.quote_plus(category)
        encoded_location = urllib.parse.quote_plus(location)
        
        for page in range(max_pages):
            start = page * 10  # Yelp shows 10 results per page
            search_url = f"https://www.yelp.com/search?find_desc={encoded_category}&find_loc={encoded_location}&start={start}"
            
            print(f"Searching page {page + 1}: {search_url}")
            driver.get(search_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Try multiple selectors for business links
            business_links = []
            selectors = [
                "a[href*='/biz/']",
                "a[data-analytics-label='biz-name']",
                "h3 a[href*='/biz/']",
                ".businessName a"
            ]
            
            for selector in selectors:
                try:
                    links = driver.find_elements(By.CSS_SELECTOR, selector)
                    if links:
                        business_links = links
                        print(f"Found links using selector: {selector}")
                        break
                except:
                    continue
            
            page_urls = []
            for link in business_links:
                href = link.get_attribute('href')
                if href and '/biz/' in href:
                    # Clean the URL to remove query parameters
                    clean_url = href.split('?')[0]
                    if clean_url not in business_urls:
                        business_urls.append(clean_url)
                        page_urls.append(clean_url)
            
            print(f"Found {len(page_urls)} businesses on page {page + 1}")
            
            # If no results found, try to debug
            if len(page_urls) == 0:
                print("No businesses found on this page. Checking page content...")
                try:
                    page_source = driver.page_source
                    if "No businesses found" in page_source or "0 results" in page_source:
                        print("Yelp returned no results for this search.")
                        break
                    elif "blocked" in page_source.lower() or "captcha" in page_source.lower():
                        print("May be blocked by Yelp. Trying to continue...")
                except:
                    pass
            
            # Random delay between pages
            if page < max_pages - 1:
                delay = random.uniform(3, 6)
                print(f"Waiting {delay:.1f} seconds before next page...")
                time.sleep(delay)
    
    except Exception as e:
        print(f"Error during search: {str(e)}")
    
    print(f"\nTotal businesses found: {len(business_urls)}")
    return business_urls

def extract_rating(driver):
    """Extract business rating"""
    try:
        rating_selectors = [
            "div[data-testid='rating'] span.y-css-qn4gww",
            ".y-css-qn4gww[aria-label*='star rating']",
            "span[aria-label*='star rating']",
            "div[role='img'][aria-label*='star rating']"
        ]
        
        for selector in rating_selectors:
            try:
                rating_element = driver.find_element(By.CSS_SELECTOR, selector)
                rating_text = rating_element.get_attribute('aria-label') or rating_element.text
                if rating_text:
                    # Extract number from rating text
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        return rating_match.group(1)
            except:
                continue
        return "N/A"
    except Exception as e:
        print(f"Error extracting rating: {e}")
        return "N/A"

def extract_review_count(driver):
    """Extract number of reviews"""
    try:
        review_selectors = [
            "span.y-css-qn4gww[aria-label*='review']",
            "a[href*='#reviews'] span",
            "span[data-font-weight='semibold'][aria-label*='review']",
            "span.reviewCount"
        ]
        
        for selector in review_selectors:
            try:
                review_element = driver.find_element(By.CSS_SELECTOR, selector)
                review_text = review_element.get_attribute('aria-label') or review_element.text
                if review_text:
                    # Extract number from review text
                    review_match = re.search(r'(\d+)', review_text.replace(',', ''))
                    if review_match:
                        return review_match.group(1)
            except:
                continue
        return "N/A"
    except Exception as e:
        print(f"Error extracting review count: {e}")
        return "N/A"

def extract_address(driver):
    """Extract business address"""
    try:
        address_selectors = [
            "p[data-testid='address']",
            "address p",
            "div[data-testid='business-location'] p",
            "p.y-css-qn4gww[data-font-weight='normal']"
        ]
        
        for selector in address_selectors:
            try:
                address_element = driver.find_element(By.CSS_SELECTOR, selector)
                address_text = address_element.text.strip()
                if address_text and len(address_text) > 5:  # Basic validation
                    return address_text
            except:
                continue
        return "N/A"
    except Exception as e:
        print(f"Error extracting address: {e}")
        return "N/A"

def extract_phone_number(driver):
    """Extract business phone number"""
    try:
        phone_selectors = [
            "section.y-css-1790tv2 div.y-css-4cg16w:nth-of-type(2) p.y-css-qn4gww[data-font-weight='semibold']",
            "section.y-css-1790tv2 div.y-css-4cg16w:nth-of-type(1) p.y-css-qn4gww[data-font-weight='semibold']",
            "section.y-css-1790tv2 div.y-css-4cg16w:nth-of-type(3) p.y-css-qn4gww[data-font-weight='semibold']",
            "p[data-testid='phone-number']",
            "a[href^='tel:']"
        ]
        
        for selector in phone_selectors:
            try:
                phone_element = driver.find_element(By.CSS_SELECTOR, selector)
                phone_text = phone_element.text.strip()
                # Validate it's actually a phone number
                if phone_text and any(char.isdigit() for char in phone_text) and \
                   ('(' in phone_text or '-' in phone_text or len([c for c in phone_text if c.isdigit()]) >= 10):
                    return phone_text
            except:
                continue
        return "N/A"
    except Exception as e:
        print(f"Error extracting phone number: {e}")
        return "N/A"

def extract_website(driver):
    """Extract business website"""
    try:
        website_selectors = [
            "a[data-testid='website-link']",
            "a[href*='http']:not([href*='yelp.com'])",
            "section.y-css-1790tv2 a[href^='http']"
        ]
        
        for selector in website_selectors:
            try:
                website_element = driver.find_element(By.CSS_SELECTOR, selector)
                website_url = website_element.get_attribute('href')
                if website_url and not 'yelp.com' in website_url:
                    return website_url
            except:
                continue
        return "N/A"
    except Exception as e:
        print(f"Error extracting website: {e}")
        return "N/A"

def extract_business_hours(driver):
    """Extract business hours"""
    try:
        hours_selectors = [
            "div[data-testid='hours'] tbody tr",
            "table.hours-table tbody tr",
            "div.hours-table tbody tr"
        ]
        
        hours_data = []
        for selector in hours_selectors:
            try:
                hour_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if hour_elements:
                    for element in hour_elements:
                        hours_text = element.text.strip()
                        if hours_text:
                            hours_data.append(hours_text)
                    if hours_data:
                        return "; ".join(hours_data)
            except:
                continue
        return "N/A"
    except Exception as e:
        print(f"Error extracting business hours: {e}")
        return "N/A"

def extract_categories(driver):
    """Extract business categories"""
    try:
        category_selectors = [
            "span.y-css-qn4gww a[href*='/c/']",
            "a[href*='/categories/']",
            "div[data-testid='categories'] a"
        ]
        
        categories = []
        for selector in category_selectors:
            try:
                category_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in category_elements:
                    category_text = element.text.strip()
                    if category_text and category_text not in categories:
                        categories.append(category_text)
            except:
                continue
        
        return ", ".join(categories) if categories else "N/A"
    except Exception as e:
        print(f"Error extracting categories: {e}")
        return "N/A"

def extract_price_range(driver):
    """Extract price range ($ symbols)"""
    try:
        price_selectors = [
            "span.y-css-qn4gww[aria-label*='price range']",
            "span[data-testid='price-range']",
            "span.price-range"
        ]
        
        for selector in price_selectors:
            try:
                price_element = driver.find_element(By.CSS_SELECTOR, selector)
                price_text = price_element.get_attribute('aria-label') or price_element.text
                if price_text and '$' in price_text:
                    return price_text.strip()
            except:
                continue
        return "N/A"
    except Exception as e:
        print(f"Error extracting price range: {e}")
        return "N/A"

def scrape_business_info(driver, url):
    """Main function to scrape all business information"""
    try:
        print(f"\nScraping: {url}")
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
        )
        
        # Extract business name
        try:
            business_name = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
        except:
            business_name = "N/A"
        
        # Extract all information
        business_info = {
            'business_name': business_name,
            'rating': extract_rating(driver),
            'review_count': extract_review_count(driver),
            'address': extract_address(driver),
            'phone': extract_phone_number(driver),
            'website': extract_website(driver),
            'categories': extract_categories(driver),
            'price_range': extract_price_range(driver),
            'business_hours': extract_business_hours(driver),
            'yelp_url': url
        }
        
        # Print extracted info
        print(f"Business: {business_info['business_name']}")
        print(f"Rating: {business_info['rating']}")
        print(f"Reviews: {business_info['review_count']}")
        print(f"Phone: {business_info['phone']}")
        print(f"Address: {business_info['address']}")
        print(f"Categories: {business_info['categories']}")
        
        return business_info
        
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return {
            'business_name': 'N/A',
            'rating': 'N/A',
            'review_count': 'N/A',
            'address': 'N/A',
            'phone': 'N/A',
            'website': 'N/A',
            'categories': 'N/A',
            'price_range': 'N/A',
            'business_hours': 'N/A',
            'yelp_url': url
        }

def main():
    """Main function to run the scraper"""
    print("="*60)
    print("           YELP BUSINESS SEARCH SCRAPER")
    print("="*60)
    print("This tool will search Yelp for businesses and extract their information")
    print()
    
    # Get user input
    category = input("Enter business category (e.g., 'restaurants', 'pizza', 'dentist'): ").strip()
    if not category:
        print("Error: Business category is required!")
        return
    
    location = input("Enter location (e.g., 'New York, NY', 'Los Angeles, CA'): ").strip()
    if not location:
        print("Error: Location is required!")
        return
    
    # Get number of pages to scrape
    try:
        max_pages = input("How many pages to scrape? (default: 3, max: 10): ").strip()
        max_pages = int(max_pages) if max_pages else 3
        max_pages = min(max_pages, 10)  # Limit to 10 pages
    except ValueError:
        max_pages = 3
    
    # Generate output filename
    safe_category = re.sub(r'[^\w\s-]', '', category).strip().replace(' ', '_')
    safe_location = re.sub(r'[^\w\s-]', '', location).strip().replace(' ', '_')
    output_file = f"yelp_{safe_category}_{safe_location}.csv"
    
    print(f"\nSearching for '{category}' businesses in '{location}'...")
    print(f"Will scrape up to {max_pages} pages of results")
    print(f"Results will be saved to: {output_file}")
    print("\nStarting search...")
    
    driver = get_driver()
    
    try:
        # Search for businesses
        business_urls = search_yelp_businesses(driver, category, location, max_pages)
        
        if not business_urls:
            print("No businesses found for the given search criteria.")
            return
        
        print(f"\nFound {len(business_urls)} businesses. Starting detailed scraping...")
        
        # Create CSV file and write header
        fieldnames = [
            'business_name', 'rating', 'review_count', 'address', 
            'phone', 'website', 'categories', 'price_range', 
            'business_hours', 'yelp_url'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Scrape each business
            for i, url in enumerate(business_urls, 1):
                print(f"\n[{i}/{len(business_urls)}] Processing business...")
                business_info = scrape_business_info(driver, url)
                writer.writerow(business_info)
                
                # Random delay between requests (except for last one)
                if i < len(business_urls):
                    delay = random.uniform(3, 7)
                    print(f"Waiting {delay:.1f} seconds before next request...")
                    time.sleep(delay)
        
        print(f"\n{'='*60}")
        print(f"SCRAPING COMPLETE!")
        print(f"{'='*60}")
        print(f"✅ Successfully scraped {len(business_urls)} businesses")
        print(f"📁 Data saved to: {output_file}")
        print(f"🔍 Search: {category} in {location}")
        print(f"{'='*60}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    # Check and install required packages
    try:
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        print("Installing required packages...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "webdriver-manager"])
        # Import again after installation
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
    
    main()
