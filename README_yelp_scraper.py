"""
YELP SEARCH SCRAPER DEMO

This script demonstrates how to use the Yelp Search Scraper.

HOW TO USE:
1. Run: python yelp_search_scraper.py
2. Enter business category (e.g., 'pizza', 'dentist', 'restaurants')
3. Enter location (e.g., 'New York, NY', 'Los Angeles, CA')
4. Enter number of pages to scrape (optional, default is 3)

EXAMPLE USAGE:
- Category: pizza
- Location: New York, NY
- Pages: 2

The scraper will:
1. Search Yelp for "pizza" businesses in "New York, NY"
2. Extract business URLs from 2 pages of search results
3. Visit each business page and extract:
   - Business name
   - Rating and review count
   - Address and phone number
   - Website and categories
   - Price range and business hours
4. Save all data to a CSV file named: yelp_pizza_New_York_NY.csv

FEATURES:
- Automatic package installation (selenium, webdriver-manager)
- Anti-detection measures to avoid being blocked
- Multiple CSS selector strategies for reliable data extraction
- Comprehensive error handling
- Random delays between requests to be respectful
- Clean output filename generation

SAMPLE OUTPUT CSV COLUMNS:
- business_name: "Joe's Pizza"
- rating: "4.5"
- review_count: "234"
- address: "123 Main St, New York, NY 10001"
- phone: "(555) 123-4567"
- website: "https://joespizza.com"
- categories: "Pizza, Italian, Fast Food"
- price_range: "$$"
- business_hours: "Mon-Sun: 11:00 AM - 11:00 PM"
- yelp_url: "https://www.yelp.com/biz/joes-pizza-new-york"
"""

print(__doc__)
