import scrapy
import json
import os

class ConferenceSpider(scrapy.Spider):
    name = 'conference_spider'
    allowed_domains = ['portal.core.edu.au']
    start_urls = ['https://portal.core.edu.au/conf-ranks/']

    def __init__(self, conference_name=None, *args, **kwargs):
        super(ConferenceSpider, self).__init__(*args, **kwargs)
        self.conference_name = conference_name
        self.results = []
        self.filename = 'conference_results.txt'
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def parse(self, response):
        search_url = f"https://portal.core.edu.au/conf-ranks/?search={self.conference_name}&by=all&source=all&sort=atitle&page=1"
        yield scrapy.Request(search_url, callback=self.parse_core_results)

    def parse_core_results(self, response):
        rows = response.xpath('//table//tr')
        
        for row in rows:
            conference = row.xpath('.//td[1]/text()').get()
            if conference and self.conference_name.lower() in conference.lower():
                data = row.xpath('.//td/text()').getall()
                result = {
                    'Title': data[0].strip(),
                    'Acronym': data[1].strip(),
                    'Source': data[2].strip(),
                    'Rank': data[3].strip(),
                    'Note': data[4].strip(),
                    'DBLP': data[5].strip(),
                    'Primary FoR': data[6].strip(),
                    'Comments': data[7].strip(),
                    'Average Rating': data[8].strip()
                }
                self.results.append(result)

    def closed(self, reason):
        with open(self.filename, 'w', encoding='utf-8') as f:
            for result in self.results:
                f.write(json.dumps(result) + '\n')
        print("ConferenceSpider has finished its work.")
