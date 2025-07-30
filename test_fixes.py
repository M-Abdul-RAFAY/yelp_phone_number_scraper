#!/usr/bin/env python3
"""
Test script to verify the fixes made to the Yelp scraper
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yelp_search_scraper import search_yelp_businesses, get_driver, scrape_business_info

def test_scraper_fixes():
    """Test the scraper with the recent fixes"""
    print("Testing Yelp Scraper with Recent Fixes")
    print("=" * 50)
    
    # Test parameters
    category = "restaurants"
    location = "New York, NY"
    max_pages = 1  # Just test one page
    
    print(f"Searching for: {category}")
    print(f"Location: {location}")
    print(f"Max pages: {max_pages}")
    print()
    
    driver = None
    try:
        # Get driver
        print("Setting up browser...")
        driver = get_driver()
        
        # Run the search
        print("Starting search...")
        business_urls = search_yelp_businesses(driver, category, location, max_pages)
        
        if business_urls:
            print(f"\nFound {len(business_urls)} business URLs!")
            print("\nTesting detailed scraping on first few businesses...")
            print("-" * 50)
            
            # Test detailed scraping on first few businesses
            for i, url in enumerate(business_urls[:3], 1):  # Test first 3
                print(f"\n{i}. Testing URL: {url}")
                business_info = scrape_business_info(driver, url)
                
                print(f"   Name: {business_info.get('business_name', 'N/A')}")
                print(f"   Rating: {business_info.get('rating', 'N/A')}")
                print(f"   Reviews: {business_info.get('review_count', 'N/A')}")
                print(f"   Website: {business_info.get('website', 'N/A')}")
                print(f"   Phone: {business_info.get('phone', 'N/A')}")
                print(f"   Address: {business_info.get('address', 'N/A')}")
                
        else:
            print("No business URLs found or search failed")
            
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            print("\nClosing browser...")
            driver.quit()

if __name__ == "__main__":
    test_scraper_fixes()
