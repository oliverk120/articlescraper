import scrapy
import csv
import json
import uuid  # Import the uuid module
from urllib.parse import urlsplit

class ForbesArticleScraper(scrapy.Spider):
    name = "forbes_article_scraper"
    start_urls = [
        'https://www.forbes.com/vetted/gifts/holiday/', # Forbes Gifts URL
    ]

    def parse(self, response):
        # Extract the article link from the page using the specified selector
        article_links = response.css('article.stream-item h3 a::attr(href)').getall()

        # Yield the article links as dictionary items
        for link in article_links:
            yield {'link': link}

# Run the spider and export the data to a CSV file
# scrapy crawl forbes_article_scraper -o forbes_article_links.csv

class ForbesArticleDetailsScraper(scrapy.Spider):
    name = "forbes_article_details_scraper"
    
    # List of article links to scrape
    article_links = []
    # Read the list of links from the CSV file
    with open('forbes_article_links.csv', newline='') as csvfile:
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
        body_text = response.css('div.article-body-container p::text').get()
        article_date = response.css('time::text').get()
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
# scrapy crawl forbes_article_details_scraper -o forbes_article_details.csv

class ForbesGiftScraper(scrapy.Spider):
    name = 'forbes_gift_scraper'
    # List of article links to scrape
    article_links = [] # Update this with the list of links you have
    # Read the list of links from the CSV file
    with open('forbes_article_links.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            article_links.append(row['link'])

    def start_requests(self):
        # Start requests for each article link
        for link in self.article_links:
            yield scrapy.Request(url=link, callback=self.parse)

    def parse(self, response):
        # Create a selector for the individual product within the page
        products = response.css('div.finds-module-wrapper')
        # Loop through each product
        for product in products:
            # Extract price information
            price = product.css('fbs-pricing::attr(sale-price)').get()

            # Select the fbs-pricing element and extract the embed-data attribute value
            embed_data_str = response.css('fbs-pricing::attr(embed-data)').get()
            
            # Parse the JSON string
            embed_data = json.loads(embed_data_str)
            # Populate gift item
            gift_item = {}
            gift_item['id'] = str(uuid.uuid4())  # Generate a unique ID
            gift_item['name'] = product.css('h3.finds-module-title::text').get()
            gift_item['image_url'] = product.css('progressive-image::attr(src)').get()
            gift_item['product_source_url'] = product.css('a.embed-base.finds-embed::attr(href)').get()
            gift_item['description'] = product.css('div.finds-module-description p::text').get()
            gift_item['price'] = price
            gift_item['giftsource_url'] = response.url
            gift_item['start_url'] = response.url
            # Extract the vendorName field from the parsed JSON object
            gift_item['brand'] = embed_data.get('vendorName')

            # Check if the 'name' exists, and only yield the gift_item if it does
            if gift_item['name'] is not None:
                yield gift_item

# Run the spider and export the data to a CSV file
# scrapy crawl forbes_gift_scraper -o forbes_gifts.csv
