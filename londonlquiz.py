import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from ..items import Property


class LondonSpider(scrapy.Spider):
    name = 'londonquiz'
    allowed_domains = ['londonrelocation.com']
    start_urls = ['https://londonrelocation.com/properties-to-rent/']

    def parse(self, response):
        for start_url in self.start_urls:
            yield Request(url=start_url,
                        callback=self.parse_area)

    def parse_area(self, response):
        area_urls = response.xpath('.//div[contains(@class,"area-box-pdh")]//h4/a/@href').extract()
        for area_url in area_urls:
            yield Request(url=area_url,
                        callback=self.parse_area_pages)

    def parse_area_pages(self, response):
        div_father = response.xpath("//div[@class='test-box']")
        for container in div_father :
            title = container.xpath("normalize-space(.//div[@class='h4-space']/h4/a/text())").get()
            price = container.xpath(".//div[@class='bottom-ic']/h5/text()").get()
            link = container.xpath(".//div[@class='h4-space']/h4/a/@href").get()
            ab_link = response.urljoin(link)
            property = ItemLoader(item=Property(), selector=container)
            property.add_value('title', title)
            property.add_value('price', price)
            property.add_value('link', ab_link)
            yield property.load_item()

            page_after = response.xpath("(//div[@class='pagination']/ul/li)[3]/a/@href").get()

            if page_after:
                yield Request(url=page_after, callback=self.parse_area_pages)