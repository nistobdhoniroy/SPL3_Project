import difflib
from .models import Product, ProductRating
from ecommerce_products.models import OtherProduct
import pandas as pd
# from scipy import sparse
# from sklearn.metrics.pairwise import cosine_similarity
#

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
    # print(text1 + 'is: ' + str(difference))
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


# Returns a list
def get_real_vendor_similar_prods(product_name):
    all_products = OtherProduct.objects.all()
    threshold = 0.85
    similar_dictionary = []
    for product in all_products:
        if similarity_value(product.title, product_name) > threshold:
            similar_dictionary.append(product)

    return similar_dictionary


def get_similar(corrMatrix, product_id, rating):
    similar_ratings = corrMatrix[product_id]*(rating-2.5)
    similar_ratings = similar_ratings.sort_values(ascending=False)
    return similar_ratings


def recommendation_product(ratingsQuery):

    all_product_rating = pd.DataFrame(list(ProductRating.objects.all().values()))

    user_ratings = all_product_rating.pivot_table(index=['product_id'], columns=['user_id'], values='rating')

    user_ratings = user_ratings.T

    user_ratings = user_ratings.dropna(thresh=1, axis=1).fillna(0, axis=1)

    corr_matrix = user_ratings.corr(method='pearson')

    similar_products = pd.DataFrame()

    items = dict()
    try:
        for query_product in ratingsQuery:
            similar_products = similar_products.append(get_similar(corr_matrix, query_product.product_id, query_product.rating), ignore_index=True)

        result = similar_products.sum().sort_values(ascending=False)

        query_index = list(result.index.values)
        query_result = list(result)

        i = 0

        for index in query_index:
            # print(index, " ki re vai ", query_result[i])
            items[index] = query_result[i]
            i = i+1

        # print(items)
        # print(result)
        # print(query_result)
        return items

    except:
        return items


def standardize(row):
    new_row = (row - row.mean())/(row.max()-row.min())
    return new_row

#
# def recTest(ratingsQuery):
#     all_product_rating = pd.DataFrame(list(ProductRating.objects.all().values()))
#     user_ratings = all_product_rating.pivot_table(index=['product_id'], columns=['user_id'], values='rating')
#
#     ratings = user_ratings.fillna(0)
#     print(ratings)
#     #
#     df_std = ratings.apply(standardize).T
#
#     print(df_std)
#
#     sparse_df = sparse.csr_matrix(df_std.values)
#     corrMatrix = pd.DataFrame(cosine_similarity(sparse_df), index=ratings.columns, columns=ratings.columns)
#     #
#     print("corrMatrix")
#     print(corrMatrix)
#
#     return 1
