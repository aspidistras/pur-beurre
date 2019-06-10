import requests
import json
from .constants import CATEGORIES_LIST_URL, PRODUCTS_LIST_URL, SCORES_LIST
from .models import Category, Product


def access_url(url):
    request = requests.get(url)
    result = json.loads(request.text)
    return result


def get_categories():
    categories_list = access_url(CATEGORIES_LIST_URL)
    for category in categories_list['tags']:
        category = Category.objects.create(name=categories_list['tags'][category]['name'])
        category.save()


def get_products():
    for score in SCORES_LIST:
        products_list = access_url(PRODUCTS_LIST_URL.format(score))
        for product in products_list['products']:
            product = Product.objects.create(name=products_list['products'][product]
                                                ['product_name_fr'],
                                             score=products_list['products'][product]
                                                ['nutrition_grades'])
            product.save()
            for category in products_list['products'][product]['categories_tags']:
                product.category_id.add(category)
                product.save()


