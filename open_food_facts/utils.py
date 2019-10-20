"""methods to access and manage data module"""

import json
import requests

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import DataError
from django.core.exceptions import ValidationError

from .constants import CATEGORIES_LIST_URL, PRODUCTS_LIST_URL, SCORES_LIST, SCORE_IMAGES_LIST, \
    MAX_PAGES_NUMBER
# uncomment to get all products
# from .constants import PRODUCTS_INFO_URL
from .models import Category, Product, Substitute, User


def access_url(url):
    """returns json result when accessing an url"""

    request = requests.get(url)
    result = json.loads(request.text)
    return result


def get_products():
    """accesses Open Food Facts data and fills database with products"""

    print("Produits en cours d'ajout à la base de données...")

    for score, score_image_url in zip(SCORES_LIST, SCORE_IMAGES_LIST):

        # uncomment and replace MAX_PAGES_NUMBER by pages_count to get all products
        # products_list_info = access_url(PRODUCTS_INFO_URL.format(score))
        # pages_count = int(products_list_info['count'] / 20 + 1)

        for page in range(1, MAX_PAGES_NUMBER):
            products_list = access_url(PRODUCTS_LIST_URL.format(score, page))
            for i, product in enumerate(products_list['products']):
                try:
                    if products_list['products'][i]['product_name_fr'] and not \
                            Product.objects.filter(
                                name=products_list['products'][i]['product_name_fr']).exists():
                        product = Product.objects.create(
                            name=products_list['products'][i]['product_name_fr'],
                            score=products_list['products'][i]['nutrition_grades'],
                            score_image=score_image_url)
                        product.image = products_list['products'][i]['image_small_url']
                        product.calories = \
                            products_list['products'][i]['nutriments']['energy_value']
                        product.fats = products_list['products'][i]['nutriments']['fat_100g']
                        product.carbs = \
                            products_list['products'][i]['nutriments']['carbohydrates_100g']
                        product.proteins = \
                            products_list['products'][i]['nutriments']['proteins_100g']
                        product.salt = products_list['products'][i]['nutriments']['sodium_100g']
                        product.url = products_list['products'][i]['url']
                        product.clean_fields()
                        product.save()
                        for cat in products_list['products'][i]['categories_tags']:
                            category = Category.objects.filter(tag=cat)
                            product.categories.add(*category)
                            product.clean_fields()
                            product.save()

                except KeyError or DataError or ValidationError:
                    continue

    print("Tous les produits ont été ajoutés à la base de données !")


def get_categories():
    """accesses Open Food Facts data and fills database with categories"""

    print("Catégories en cours d'ajout à la base de données...")

    categories_list = access_url(CATEGORIES_LIST_URL)
    for i, category in enumerate(categories_list['tags']):
        if categories_list['tags'][i]['name'] and categories_list['tags'][i]['id'] and not \
                Category.objects.filter(name=categories_list['tags'][i]['name']).exists():
            category = Category.objects.create(name=categories_list['tags'][i]['name'],
                                               tag=categories_list['tags'][i]['id'])
            category.save()

    print("Toutes les catégories ont été ajoutées à la base de données !")


def get_products_search(request):
    """searches product matching the user's request"""

    global PRODUCTS_LIST
    global QUERY

    if request.method == "POST":
        query = request.POST.get('search')

        if query:
            PRODUCTS_LIST = Product.objects.filter(name__icontains=query).order_by('name')
            QUERY = query

    return display_products(request, PRODUCTS_LIST, QUERY)


def get_substitutes(request, product_id):
    """finds substitutes matching the user's chosen product"""

    product = Product.objects.get(pk=product_id)
    categories = product.categories.values_list('id', flat=True)
    categories_list = list(categories)

    temporary_substitutes = list(Product.objects.filter(score__lte=product.score).filter(
        categories__in=categories).order_by('score').exclude(id=product_id))

    categories_occurrence_dict = dict()

    for product in temporary_substitutes:
        categories_occurrence_dict[product.id] = 0
        substitutes_categories_list = list(product.categories.values_list('id', flat=True))
        for i in categories_list:
            for cat in substitutes_categories_list:
                if cat == i:
                    categories_occurrence_dict[product.id] += 1

    sorted_substitutes = sorted(categories_occurrence_dict.items(), key=lambda x: x[1],
                                reverse=True)[:12]

    substitutes_id_list = list(map(lambda x: x[0], sorted_substitutes))

    substitutes_list = Product.objects.filter(id__in=substitutes_id_list)

    return display_products(request, substitutes_list, query=None)


def get_saved_substitutes(request):
    """finds the user's saved products"""

    user = User.objects.get(pk=request.user.id)
    substitutes_id_list = Substitute.objects.filter(user=user).values_list('id')
    substitutes_list = Product.objects.filter(id__in=substitutes_id_list).order_by('id')
    return display_products(request, substitutes_list, query=None)


def display_products(request, products_list, query):
    """returns context to be displayed by template with paginated products list"""

    paginator = Paginator(products_list, 6)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)

    context = {
        'products': products,
        'search': query,
        'paginate': True,
    }

    return context
