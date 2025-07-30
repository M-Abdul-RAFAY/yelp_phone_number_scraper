#!/usr/bin/env python3
"""
Test script for the improved Yelp scraper
This script tests individual extraction functions
"""

import sys
from yelp_search_scraper import get_driver, scrape_business_info

def test_single_business():
    """Test scraping a single business"""
    print("Testing improved Yelp scraper...")
    print("="*50)
    
    # Test URL - a popular restaurant in NYC
    test_url = "https://www.yelp.com/biz/katzs-delicatessen-new-york"
    
    driver = get_driver()
    
    try:
        print(f"Testing extraction functions on: {test_url}")
        result = scrape_business_info(driver, test_url)
        
        print("\n" + "="*50)
        print("EXTRACTION RESULTS:")
        print("="*50)
        
        for key, value in result.items():
            if key != 'yelp_url':
                status = "✅" if value != "N/A" else "❌"
                print(f"{status} {key.replace('_', ' ').title()}: {value}")
        
        # Count successful extractions
        successful = sum(1 for v in result.values() if v != "N/A" and v != test_url)
        total = len(result) - 1  # Exclude URL from count
        
        print(f"\n📊 Success Rate: {successful}/{total} fields extracted ({successful/total*100:.1f}%)")
        
        if successful < 5:
            print("\n⚠️  Low success rate. The website structure may have changed.")
            print("Consider updating the CSS selectors in the extraction functions.")
        else:
            print("\n🎉 Good success rate! The scraper is working well.")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_single_business()
