import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver

def scrape_phone_number(driver, url):
    try:
        driver.get(url)
        
        # Wait for the contact section to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "section.y-css-1790tv2"))
            )
            
            # First find the phone icon element
            phone_icon = driver.find_element(
                By.CSS_SELECTOR,
                "svg[aria-label='Business phone number']"
            )
            
            # Then navigate to the phone number element
            phone_element = phone_icon.find_element(
                By.XPATH,
                "./ancestor::div[contains(@class, 'css-')]/following-sibling::div//p[contains(@class, 'y-css-qn4gww')]"
            )
            
            if phone_element:
                return phone_element.text.strip()
            
        except Exception as e:
            print(f"Couldn't find phone number in expected format: {str(e)}")
            
            # Fallback: Try direct CSS selector
            try:
                phone_element = driver.find_element(
                    By.CSS_SELECTOR,
                    "section.y-css-1790tv2 div.y-css-4cg16w:nth-of-type(2) p.y-css-qn4gww[data-font-weight='semibold']"
                )
                if phone_element:
                    return phone_element.text.strip()
            except:
                pass
            
            return "N/A"
        
    except Exception as e:
        print(f"Error loading page {url}: {str(e)}")
        return "N/A"

def process_csv(input_file, output_file):
    # Check if input file exists
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
            fieldnames = list(reader.fieldnames)
            
            # Add 'phone' column if it doesn't exist
            if 'phone' not in fieldnames:
                fieldnames.append('phone')
            
            writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=dialect.delimiter)
            writer.writeheader()
            
            for row in reader:
                url = row.get('url') or row.get('URL') or row.get('website')
                if url and url.strip() and url.strip().upper() != "N/A":
                    print(f"\nProcessing: {url}")
                    phone = scrape_phone_number(driver, url)
                    row['phone'] = phone if phone else "N/A"
                    print(f"Found phone: {row['phone']}")
                    
                    delay = random.uniform(5, 15)
                    print(f"Waiting {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    # Set phone to N/A for rows without URLs
                    row['phone'] = "N/A"
                
                writer.writerow(row)
    
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
        print("Usage: python yelp_selenium.py <input_filename.csv> [output_filename.csv]")
        sys.exit(1)
        
    input_csv = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else 'output_with_phones_selenium.csv'
    
    try:
        from selenium import webdriver
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "webdriver-manager"])
        from selenium import webdriver
    
    process_csv(input_csv, output_csv)
    print(f"\nProcessing complete. Results saved to {output_csv}")