import scrapy
import csv
import uuid  # Import the uuid module
from urllib.parse import urlsplit

class BusinessInsiderArticleScraper(scrapy.Spider):
    name = "business_insider_article_scraper"
    start_urls = [
        'https://www.businessinsider.com/guides/gifts', # Business Insider Gifts URL
    ]

    def parse(self, response):
        # Extract the relative article links from the h3 element with class 'tout-title'
        relative_article_links = response.css('h3.tout-title a.tout-title-link::attr(href)').getall()
        
        # Make the links full URLs by joining the base URL with the relative URLs
        base_url = 'https://www.businessinsider.com'
        article_links = [base_url + relative_link for relative_link in relative_article_links]

        # Yield the article links as dictionary items
        for link in article_links:
            yield {'link': link}

# Run the spider and export the data to a CSV file
# scrapy crawl business_insider_article_scraper -o business_insider_article_links.csv

class BusinessInsiderArticleDetailsScraper(scrapy.Spider):
    name = "business_insider_article_details_scraper"
    
    # List of article links to scrape
    article_links = []
    # Read the list of links from the CSV file
    with open('business_insider_article_links.csv', newline='') as csvfile:
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
        body_text = ' '.join(response.css('div.content-lock-content p::text').getall())
        datetime_string = response.css('div.byline-timestamp::text').get()
        if datetime_string:
            datetime_string = datetime_string.strip()
        article_date = datetime_string
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
# scrapy crawl business_insider_gifts_article_scraper -o business_insider_article_details.csv

class BusinessInsiderGiftScraper(scrapy.Spider):
    name = 'business_insider_gift_scraper'
    # List of article links to scrape
    article_links = [] # Update this with the list of links you have
    # Read the list of links from the CSV file
    with open('business_insider_article_links.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            article_links.append(row['link'])

    def start_requests(self):
        # Start requests for each article link
        for link in self.article_links:
            yield scrapy.Request(url=link, callback=self.parse)

    def parse(self, response):
        # Create a selector for all individual products within the page
        products = response.css('li.product-grid-item')

        # Loop through each product
        for product in products:
            # Extract price information
            price_text = product.css('a.product-grid-button::text').get()
            price = price_text.strip('$').split(' ')[0] if price_text else None  # Remove "$" from the price text

            # Populate gift item
            gift_item = {}
            gift_item['id'] = str(uuid.uuid4())  # Generate a unique ID
            gift_item['name'] = product.css('div.product-grid-heading a::text').get().strip()
            gift_item['image_url'] = product.css('noscript img::attr(src)').get()
            gift_item['brand'] = product.css('div.product-grid-subheading::text').get()
            gift_item['product_source_url'] = product.css('a.product-grid-button::attr(href)').get()
            gift_item['description'] = product.css('div.product-grid-content::text').get()
            gift_item['price'] = price
            gift_item['giftsource_url'] = response.url
            gift_item['start_url'] = response.url

            # Check if the 'name' exists, and only yield the gift_item if it does
            if gift_item['name'] is not None:
                yield gift_item

# Run the spider and export the data to a CSV file
# scrapy crawl business_insider_gift_scraper -o business_insider_gifts.csv