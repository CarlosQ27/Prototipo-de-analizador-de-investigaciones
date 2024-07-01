import scrapy
import re
import os
from urllib.parse import urljoin

class AboutSpider(scrapy.Spider):
    name = 'about_spider'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
        'DOWNLOAD_DELAY': 2
    }

    def __init__(self, start_urls=None, *args, **kwargs):
        super(AboutSpider, self).__init__(*args, **kwargs)
        if start_urls:
            self.start_urls = start_urls
            print(f"Starting spider with URLs: {self.start_urls}")
        self.all_content = ""
        self.word_limit = 9000
        self.total_words_written = 0
        self.filename = 'about_results.txt'

        # Remove the file if it exists
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def start_requests(self):
        start_url = self.start_urls[0]
        robots_url = urljoin(start_url, '/robots.txt')
        yield scrapy.Request(robots_url, self.parse_robots_txt, meta={'start_url': start_url})

    def parse_robots_txt(self, response):
        start_url = response.meta['start_url']
        yield scrapy.Request(start_url, self.parse)

    def parse(self, response):
        keywords = ['about', 'acerca', 'aims & scope', 'aboutJournal']
        page_content = response.text

        if any(keyword in response.url.lower() for keyword in keywords) or any(keyword in page_content.lower() for keyword in keywords):
            self.log(f'Processing current page: {response.url}')
            self.parse_about_page(response)

        meta_links = re.findall(r'<meta[^>]+content="([^"]+)"', page_content, re.IGNORECASE)
        for meta_link in meta_links:
            if any(keyword in meta_link.lower() for keyword in keywords):
                self.log(f'Following meta link: {meta_link}')
                yield response.follow(meta_link, callback=self.parse_about_page)

        links = response.css('a::attr(href)').getall()
        for link in links:
            if any(keyword in link.lower() for keyword in keywords):
                self.log(f'Following page link: {link}')
                yield response.follow(link, callback=self.parse_about_page)

        extra_links = re.findall(r'href="([^"]+)"', page_content, re.IGNORECASE)
        for link in extra_links:
            if any(keyword in link.lower() for keyword in keywords):
                self.log(f'Following extra link: {link}')
                yield response.follow(link, callback=self.parse_about_page)

    def parse_about_page(self, response):
        if self.total_words_written >= self.word_limit:
            return

        self.log(f'Parsing about page: {response.url}')
        about_paragraphs = response.css('p::text').getall()

        if not about_paragraphs:
            about_paragraphs = response.css('div::text').getall()

        current_text = " ".join(paragraph.strip() for paragraph in about_paragraphs)
        current_text_words = current_text.split()
        
        remaining_words = self.word_limit - self.total_words_written
        words_to_write = current_text_words[:remaining_words]

        with open(self.filename, 'a', encoding='utf-8') as f:
            f.write(f'URL: {response.url}\n')
            f.write(" ".join(words_to_write) + '\n')
            f.write('\n')

        self.total_words_written += len(words_to_write)

    def closed(self, reason):
        self.crawler.stats.set_value('extracted_content', self.all_content)
        print("Spider has finished its work.")
