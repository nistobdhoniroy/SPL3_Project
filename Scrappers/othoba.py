import scrapy


class BagdoomSaree(scrapy.Spider):
    name = 'daraz_products'
    start_urls = [
        'https://www.othoba.com/gents-shirts',
    ]

    def parse(self, response):
        for quote in response.xpath("//div[@class='item-box']"):
            yield {
                'pr_title': quote.xpath(".//div[@class='product-item']/div[@class='details']/h2[@class='product-title']/a/text()").get(),
                #'pr_title': quote.xpath(".//div[@class='c2prKC']/div[@class='c3e8SH c2mzns']/div[@class='c5TXIP']/div[@class='c3KeDq']//div[@class='c16H9d']/a/text()").get(),
                # 'pr_price': quote.xpath(".//div[@class='price-box']/span[@class='regular-price']/span[@class='price']/text()").get(),
                # 'pr_link': quote.xpath(".//h2[@class='product-name']/a/@href").get(),
            }

        # next_page= response.xpath("//div[@class='pages']/ol/li/a[@class='next i-next']/@href").get()
        # if next_page is not None:
        #     yield response.follow(next_page, self.parse)

