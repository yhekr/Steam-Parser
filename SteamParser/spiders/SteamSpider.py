import scrapy


def format_string_spaces(string):
    return string.replace("\n", "").replace("\t", "").replace("\r", "")


def format_string_hooks(string):
    return string.replace(')', '').replace('(', "")


class SteamSpider(scrapy.Spider):
    name = 'SteamSpider'
    allowed_domains = ['store.steampowered.com']
    start_urls = ['http://store.steampowered.com/']
    queries = ['strategy', 'action', 'rpg']
    pages_count = 2

    def start_requests(self):
        for query in self.queries:
            for i in range(self.pages_count):
                url = f'https://store.steampowered.com/search/?term=' \
                      f'{query}&page={i + 1}'
                yield scrapy.Request(url, callback=self.parse_keyword_response)

    def parse_keyword_response(self, response):
        req = []
        for href in response.xpath("//div[@id='search_resultsRows']/a/@href").extract():
            req.append(href)
        for i in req:
            yield scrapy.Request(i, callback=self.parse)

    def parse(self, response):
        items = {}
        name = response.xpath('//div[@id="appHubAppName"]/text()').extract()
        category = response.xpath('//div[@class="blockbg"]/a/text()').extract()
        reviews_count = response.xpath('//div[@class="summary column"]/span[@class="responsive_hidden"]/text()').extract()
        mark = response.xpath('//div [@class="summary column"]/span[@class="nonresponsive_hidden responsive_reviewdesc"]/text()').extract()
        release_date = response.xpath('//div[@class="release_date"]/div[@class="date"]/text()').extract()
        developer = response.xpath('//div[@id="developers_list"]/a/text()').extract()
        tags = response.xpath('//a[@class="app_tag"]/text()').extract()
        price = response.xpath('//div[@class="game_purchase_price price"]/text()').extract()
        platforms = response.xpath('//div[@class="sysreq_tabs"]/div/text()').extract()
        if name != "":
            items["name"] = ''.join(name)
            items["category"] = category[1]
            items["reviews_count"] = format_string_hooks(format_string_spaces(''.join(reviews_count)).split(')(')[-1])
            items["mark"] = format_string_spaces(''.join(mark)).split('%')[0][2:]
            items["release_date"] = ''.join(release_date)
            items["developer"] = ''.join(developer)
            items["tags"] = format_string_spaces(', '.join(tags))
            items["price"] = format_string_spaces(''.join(price)).split('.')[0]
            if len(items["price"]) == 0:
                price = response.xpath('//div[@class="discount_final_price"]/text()').extract()
                items["price"] = format_string_spaces(''.join(price)).split('.')[0]
            items["platforms"] = format_string_spaces(', '.join(platforms))
            if not items["platforms"]:
                items["platforms"] = "Windows"
            yield items
