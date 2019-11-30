import json
from ecommerce_products.models import OtherProduct

with open('othoba.json') as f:
    products_json = json.load(f)

for product in products_json:
    title = product['pr_title']
    price = product['pr_price']
    link = product['pr_link']
    seller = product['seller']
    product = OtherProduct(title=title, price=price, link=link, seller=seller)
    product.save()
