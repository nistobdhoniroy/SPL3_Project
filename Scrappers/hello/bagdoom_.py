import scrapy


class BagdoomSaree(scrapy.Spider):
    name = 'bagdoom_products'
    start_urls = [
        'https://www.bagdoom.com/men/clothing/shorts.html',
        'https://www.bagdoom.com/women/clothing/saree.html?',
        # 'https://www.bagdoom.com/men/clothing/t-shirt.html',
        # 'https://www.bagdoom.com/men/clothing/jeans.html',
        # 'https://www.bagdoom.com/women/shoes/heels.html',
        # 'https://www.bagdoom.com/women/accessories/bags/clutches.html',
        # 'https://www.bagdoom.com/homeliving/home-appliances/television.html',
    ]

    def parse(self, response):
        for quote in response.xpath("//div[@class='catalog_hover']"):
            yield {
                'pr_title': quote.xpath(".//h2[@class='product-name']/a/text()").get(),
                'pr_price': quote.xpath(".//div[@class='price-box']/span[@class='regular-price']/span[@class='price']/text()").get(),
                'pr_link': quote.xpath(".//h2[@class='product-name']/a/@href").get(),
            }

        next_page= response.xpath("//div[@class='pages']/ol/li/a[@class='next i-next']/@href").get()
        #next_page = response.css('li.next a::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

