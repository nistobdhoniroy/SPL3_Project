import difflib
from .models import Product


def similarity_value(text1, text2):
    sequence = difflib.SequenceMatcher(isjunk=None, a=text1, b= text2)
    difference = sequence.ratio()
    # print(text1 + 'is: ' + str(difference))

    return difference


def test_it(product_name, product_id):
    all_products = Product.objects.all().exclude(id=product_id)
    threshold = 0.85
    similar_dictionary = []
    for product in all_products:
        if similarity_value(product.name, product_name) > threshold:
            similar_dictionary.append(product)

    # print(type(similar_dictionary))
    return similar_dictionary
