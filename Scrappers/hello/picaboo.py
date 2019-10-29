import scrapy


class Picaboo(scrapy.Spider):
    name = 'picaboo_products'
    start_urls = [
        'https://www.pickaboo.com/mobile-phone.html/',
    ]

    def parse(self, response):
        for quote in response.xpath("//li[@class='product-column item']"):
            yield {
                'pr_title': quote.xpath(
                    ".//div[@class='product-item']/div[@class='product-shop']/div[@class='f-fix']"
                    "/h2[@class='product-name newname']/a/text()").get(),

                'pr_price':  quote.xpath(
                    ".//div[@class='product-item']/div[@class='product-shop']/div[@class='f-fix']"
                    "/div[@class='text-center']/div[@class='price-box']/p[@class='special-price']"
                    "/span[@class='price']/text()").get(),

                'pr_link':  quote.xpath(
                    ".//div[@class='product-item']/div[@class='product-shop']/div[@class='f-fix']"
                    "/h2[@class='product-name newname']/a/@href").get(),

            }

        # next_page = response.xpath("//div[@class='pager']/ul/li[@class='next-page']/a/@href").get()
        # if next_page is not None:
        #     yield response.follow(next_page, self.parse)

