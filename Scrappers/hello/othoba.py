import scrapy


class Othoba(scrapy.Spider):
    name = 'othoba_products'
    start_urls = [
        'https://www.othoba.com/gents-shirts',
        'https://www.othoba.com/smartphone',
    ]

    def parse(self, response):
        for quote in response.xpath("//div[@class='item-box']"):
            yield {
                'pr_title': quote.xpath(
                    ".//div[@class='product-item']/div[@class='details']/h2[@class='product-title']/a/text()").get(),
                'pr_price':  quote.xpath(
                    ".//div[@class='product-item']/div[@class='details']/div[@class='add-info']/div[@class='prices']/span[@class='price actual-price']/text()").get(),
                'pr_link': "https://www.othoba.com/"+ quote.xpath(
                    ".//div[@class='product-item']/div[@class='details']/h2[@class='product-title']/a/@href").get(),
                'seller': 'othoba'
            }

        next_page = response.xpath("//div[@class='pager']/ul/li[@class='next-page']/a/@href").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

