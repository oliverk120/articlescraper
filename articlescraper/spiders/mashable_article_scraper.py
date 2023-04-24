import scrapy
import csv
from urllib.parse import urlsplit

class MashableGiftsScraper(scrapy.Spider):
    name = "mashable_gifts_scraper"
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
# scrapy crawl mashable_gifts_scraper -o mashable_gifts_links.csv

class MashableGiftsDetailsScraper(scrapy.Spider):
    name = "mashable_gifts_details_scraper"
    
    # List of article links to scrape
    article_links = []
    # Read the list of links from the CSV file
    with open('mashable_gifts_links.csv', newline='') as csvfile:
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
        body_text = ' '.join(response.css('article p::text').getall())
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
# scrapy crawl mashable_gifts_details_scraper -o mashable_gifts_details.csv
