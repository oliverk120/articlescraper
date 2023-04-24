import scrapy
import csv
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
