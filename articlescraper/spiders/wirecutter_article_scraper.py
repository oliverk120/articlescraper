import scrapy
import csv
import uuid
from urllib.parse import urlsplit

class WirecutterArticleScraper(scrapy.Spider):
    name = "wirecutter_article_scraper"
    start_urls = [
        'https://www.nytimes.com/wirecutter/gifts/', # Update the URL
    ]

    def parse(self, response):
        # Extract the article link from the page using a more general selector
        article_links = response.css('article h3 a::attr(href)').getall()

        # Yield the article links as dictionary items
        for link in article_links:
            yield {'link': link}

# Run the spider and export the data to a CSV file
# scrapy crawl wirecutter_article_scraper -o wirecutter_article_links.csv

class WirecutterArticleDetailsScraper(scrapy.Spider):
    name = "wirecutter_article_details_scraper"
    
    # List of article links to scrape
    article_links = [] # Update this with the list of links you have
    # Read the list of links from the CSV file
    with open('wirecutter_article_links.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            article_links.append(row['link'])

    def start_requests(self):
        # Start requests for each article link
        for link in self.article_links:
            yield scrapy.Request(url=link, callback=self.parse)

    def parse(self, response):
        # Extract the required information from each page
        start_url = response.url
        title = response.css('h1::text').get()
        body_text = response.css('article section p::text').get()
        article_date = response.css('time::attr(datetime)').get()
        gender = None # Update this based on the website content or logic
        parsed_url = urlsplit(start_url)
        source_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # Yield the extracted information as a dictionary item
        yield {
            'start_url': start_url,
            'title': title,
            'body_text': body_text,
            'article_date': article_date,
            'gender': gender,
            'source_url': source_url
        }

# Run the spider and export the data to a CSV file
# scrapy crawl wirecutter_article_details_scraper -o wirecutter_article_details.csv

class WirecutterGiftScraper(scrapy.Spider):
    name = 'wirecutter_gift_scraper'
     # List of article links to scrape
    article_links = [] # Update this with the list of links you have
    # Read the list of links from the CSV file
    with open('wirecutter_article_links.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            article_links.append(row['link'])

    def start_requests(self):
        # Start requests for each article link
        for link in self.article_links:
            yield scrapy.Request(url=link, callback=self.parse)

    def parse(self, response):
        
        # Create a selector for the specified section
        products = response.css('section')

        # Loop through each product
        for product in products:
            # Extract price information
            price_text = product.css('a[class*="product-merchant-link-button"] span::text').get()
            price = price_text.strip('$') if price_text else None  # Remove "$" from the price text

            # Populate gift item
            gift_item = {}
            gift_item['id'] = str(uuid.uuid4())  # Generate a unique ID
            gift_item['name'] = product.css('a[class="product-link"]::text').get()
            gift_item['image_url'] = product.css('img::attr(src)').get()
            gift_item['brand'] = product.css('figcaption span.wp-caption-text::text').get() 
            gift_item['product_source_url'] = product.css('a[class="product-link"]::attr(href)').get()
            gift_item['description'] = ' '.join(product.css('p::text').getall())
            gift_item['price'] = price
            gift_item['giftsource_url'] = response.url
            gift_item['start_url'] = response.url

            # Check if the 'name' exists, and only yield the gift_item if it does
            if gift_item['name'] is not None:
                yield gift_item

# Run the spider and export the data to a CSV file
# scrapy crawl wirecutter_gift_scraper -o wirecutter_gifts.csv