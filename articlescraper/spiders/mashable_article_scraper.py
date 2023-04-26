import scrapy
import csv
import uuid  # Import the uuid module
from urllib.parse import urlsplit

class MashableGiftsScraper(scrapy.Spider):
    name = "mashable_article_scraper"
    start_urls = [
        'https://mashable.com/gifts',
    ]

    def parse(self, response):
        # Extract the article link from the page using the updated CSS selector
        article_links = response.css('div.w-full div.flex a.block::attr(href)').getall()

        # Remove duplicates by converting the list of links to a set
        unique_links = set(article_links)

        # Yield the article links as dictionary items with full URLs
        for link in unique_links:
            # Filter out links that start with /ad/
            if not link.startswith('/ad/'):
                full_url = response.urljoin(link)  # Convert relative URL to absolute URL
                yield {'link': full_url}

# Run the spider and export the data to a CSV file
# scrapy crawl mashable_article_scraper -o mashable_article_links.csv

class MashableGiftsDetailsScraper(scrapy.Spider):
    name = "mashable_article_details_scraper"
    
    # List of article links to scrape
    article_links = []
    # Read the list of links from the CSV file
    with open('mashable_article_links.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            article_links.append(row['link'])

    def start_requests(self):
        # Start requests for each article link
        for link in self.article_links:
            yield scrapy.Request(url=link, callback=self.parse)

    def parse(self, response):
        # Extract the required information from each page
        unique_id = str(uuid.uuid4())  # Generate a UUID
        start_url = response.url
        title = response.css('h1::text').get()
        body_text = ' '.join(response.css('article p::text').getall())
        article_date = response.css('time::attr(datetime)').get()
        gender = None # Update this based on the website content or logic
        parsed_url = urlsplit(start_url)
        source_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # Yield the extracted information as a dictionary item
        yield {
            'unique_id': unique_id,  # Include the UUID
            'start_url': start_url,
            'title': title,
            'body_text': body_text,
            'article_date': article_date,
            'gender': gender,
            'source_url': source_url
        }

# Run the spider and export the data to a CSV file
# scrapy crawl mashable_article_details_scraper -o mashable_article_details.csv

class MashableGiftScraper(scrapy.Spider):
    name = 'mashable_gift_scraper'
    # List of article links to scrape
    article_links = [] # Update this with the list of links you have
    # Read the list of links from the CSV file
    with open('mashable_article_links.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            article_links.append(row['link'])

    def start_requests(self):
        # Start requests for each article link
        for link in self.article_links:
            yield scrapy.Request(url=link, callback=self.parse)

    def parse(self, response):
        # Create a selector for all individual products within the page
        products = response.css('div[data-ga-module="gift-guide-list"]')

        # Loop through each product
        for product in products:
            # Extract price information
            price_text = product.css('a[data-ga-action="buy-link"]::text').get()
            price = price_text.strip('$').split(' ')[0] if price_text else None  # Remove "$" from the price text

            # Populate gift item
            gift_item = {}
            gift_item['id'] = str(uuid.uuid4())  # Generate a unique ID
            gift_item['name'] = product.css('a[data-ga-action="offer-title"]::text').get()
            gift_item['image_url'] = product.css('img::attr(src)').get()
            gift_item['brand'] = product.css('div.text-xs.text-gray-600::text').get()
            gift_item['product_source_url'] = product.css('a[data-ga-action="offer-title"]::attr(href)').get()
            gift_item['description'] = ' '.join(product.css('div.editor-content::text').getall())
            gift_item['price'] = price
            gift_item['giftsource_url'] = response.url
            gift_item['start_url'] = response.url

            # Check if the 'name' exists, and only yield the gift_item if it does
            if gift_item['name'] is not None:
                yield gift_item

# Run the spider and export the data to a CSV file
# scrapy crawl mashable_gift_scraper -o mashable_gifts.csv