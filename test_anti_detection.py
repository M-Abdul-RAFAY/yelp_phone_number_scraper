#!/usr/bin/env python3
"""
Quick test script for enhanced anti-detection measures
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yelp_search_scraper import get_driver
import time
import random

def test_anti_detection():
    """Test the enhanced anti-detection measures"""
    print("🧪 Testing Enhanced Anti-Detection Measures")
    print("=" * 50)
    
    driver = None
    try:
        print("🚀 Initializing enhanced stealth browser...")
        driver = get_driver()
        
        print("✅ Browser initialized successfully!")
        print(f"📱 User Agent: {driver.execute_script('return navigator.userAgent;')}")
        print(f"🔍 Webdriver Property: {driver.execute_script('return navigator.webdriver;')}")
        print(f"📺 Screen Size: {driver.execute_script('return [screen.width, screen.height];')}")
        print(f"🌍 Languages: {driver.execute_script('return navigator.languages;')}")
        
        print("\n🏠 Testing Yelp homepage visit...")
        driver.get("https://www.yelp.com")
        time.sleep(3)
        
        print("✅ Successfully loaded Yelp homepage")
        print(f"📄 Page Title: {driver.title}")
        
        print("\n👁️ Testing human behavior simulation...")
        driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 600);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")
        
        print("✅ Human behavior simulation completed")
        
        print("\n🔍 Testing search functionality...")
        search_url = "https://www.yelp.com/search?find_desc=restaurants&find_loc=New+York%2C+NY&start=0"
        driver.get(search_url)
        time.sleep(5)
        
        page_source = driver.page_source.lower()
        if any(indicator in page_source for indicator in ['verify', 'captcha', 'robot', 'blocked']):
            print("⚠️ Bot detection triggered on search page")
            print("🔧 Manual intervention may be needed")
        else:
            print("✅ Search page loaded without bot detection")
            
        print(f"📄 Search Page Title: {driver.title}")
        
        print("\n🎯 Anti-detection test completed!")
        print("🕐 Browser will remain open for 10 seconds for manual inspection...")
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            print("🔒 Closing browser...")
            driver.quit()

if __name__ == "__main__":
    test_anti_detection()
