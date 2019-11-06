import difflib
from .models import Product


# Cosine similarity between two sentences
def Counter(m):
    j = dict()
    for word in m:
        if word in j:  # word found-- increment count
            j[word] = j[word] + 1
        else:  # word not found. Add to dictionary
            j.update({word: 1})
    return j


def sqr(a):
    i = 0.000
    while (i ** 2) < a:
        i = i + 0.000001
    return i


def take_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    n = sum([vec1[x] * vec2[x] for x in intersection])  # numerator

    sum1 = sum([vec1[x] ** 2 for x in vec1])
    sum2 = sum([vec2[x] ** 2 for x in vec2])
    d = sqr(sum1) * sqr(sum2)  # denominator

    if not d:
        return 0.0
    else:
        return float(n) / d


def text_to_vector(text):
    words = text.split()
    return Counter(words)


def get_cosine_similarity(sentence1, sentence2):
    vector1 = text_to_vector(sentence1)
    vector2 = text_to_vector(sentence2)

    cosine = take_cosine(vector1, vector2)
    # print("Cosine is: ", cosine)
    return cosine


# difflib similarity
def similarity_value(text1, text2):
    sequence = difflib.SequenceMatcher(isjunk=None, a=text1, b= text2)
    difference = sequence.ratio()
    print(text1 + 'is: ' + str(difference))
    return difference


# Returns a list
def get_similar_products(product_name, product_id):
    all_products = Product.objects.all().exclude(id=product_id)
    threshold = 0.85
    similar_dictionary = []
    for product in all_products:
        if similarity_value(product.name, product_name) > threshold:
            similar_dictionary.append(product)
        # if get_cosine_similarity(product.name, product_name) > threshold:
        #     similar_dictionary.append(product)
    return similar_dictionary
