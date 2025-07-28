import csv
import time
import random
import re
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

def extract_rating(driver):
    """Extract business rating"""
    try:
        rating_selectors = [
            "div[data-testid='rating'] span.y-css-qn4gww",
            ".y-css-qn4gww[aria-label*='star rating']",
            "span[aria-label*='star rating']"
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
            "span[data-font-weight='semibold'][aria-label*='review']"
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

def process_csv(input_file, output_file):
    """Process CSV file with Yelp URLs and extract business information"""
    import os
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return
    
    driver = get_driver()
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            
            # Detect delimiter
            first_line = infile.readline()
            if not first_line.strip():
                print("Error: Input file appears to be empty.")
                return
                
            dialect = csv.Sniffer().sniff(first_line)
            infile.seek(0)
            
            reader = csv.DictReader(infile, delimiter=dialect.delimiter)
            
            # Define output fieldnames
            output_fieldnames = [
                'business_name', 'rating', 'review_count', 'address', 
                'phone', 'website', 'categories', 'price_range', 
                'business_hours', 'yelp_url'
            ]
            
            # Add original columns if they exist
            original_fieldnames = list(reader.fieldnames) if reader.fieldnames else []
            all_fieldnames = original_fieldnames + [field for field in output_fieldnames if field not in original_fieldnames]
            
            writer = csv.DictWriter(outfile, fieldnames=all_fieldnames, delimiter=dialect.delimiter)
            writer.writeheader()
            
            processed_count = 0
            for row in reader:
                url = row.get('url') or row.get('URL') or row.get('website') or row.get('yelp_url')
                
                if url and url.strip() and url.strip().upper() != "N/A" and 'yelp.com' in url:
                    business_info = scrape_business_info(driver, url)
                    
                    # Merge original row data with scraped data
                    output_row = row.copy()
                    output_row.update(business_info)
                    
                    writer.writerow(output_row)
                    processed_count += 1
                    
                    # Random delay between requests
                    delay = random.uniform(2, 5)
                    print(f"Waiting {delay:.1f} seconds before next request...")
                    time.sleep(delay)
                    
                else:
                    # If no valid Yelp URL, still write the row with N/A values
                    output_row = row.copy()
                    for field in output_fieldnames:
                        if field not in output_row:
                            output_row[field] = "N/A"
                    writer.writerow(output_row)
            
            print(f"\nProcessed {processed_count} Yelp URLs successfully!")
    
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_file}'")
    except PermissionError:
        print(f"Error: Permission denied when accessing files")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python yelp_business_scraper.py <input_filename.csv> [output_filename.csv]")
        print("\nThis scraper extracts comprehensive business information from Yelp URLs including:")
        print("- Business name")
        print("- Rating and review count")
        print("- Address and phone number")
        print("- Website and categories")
        print("- Price range and business hours")
        sys.exit(1)
        
    input_csv = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else 'yelp_business_data.csv'
    
    # Check and install required packages
    try:
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "webdriver-manager"])
        # Import again after installation
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
    
    process_csv(input_csv, output_csv)
    print(f"\nScraping complete! Business data saved to {output_csv}")
