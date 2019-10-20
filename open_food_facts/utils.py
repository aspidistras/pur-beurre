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
    # get json result for url
    result = json.loads(request.text)
    return result


def get_products():
    """accesses Open Food Facts data and fills database with products"""

    print("Produits en cours d'ajout à la base de données...")

    # browse nutrition grades
    for score, score_image_url in zip(SCORES_LIST, SCORE_IMAGES_LIST):

        # uncomment and replace MAX_PAGES_NUMBER by pages_count to get all products
        # products_list_info = access_url(PRODUCTS_INFO_URL.format(score))
        # pages_count = int(products_list_info['count'] / 20 + 1)

        # browse pages for each nutrition grade
        for page in range(1, MAX_PAGES_NUMBER):
            # get products list for each page
            products_list = access_url(PRODUCTS_LIST_URL.format(score, page))
            # browse products
            for i, product in enumerate(products_list['products']):
                try:
                    # create Product instance if product doesn't already exist and has a french name
                    if products_list['products'][i]['product_name_fr'] and not \
                            Product.objects.filter(
                                name=products_list['products'][i]['product_name_fr']).exists():
                        product = Product.objects.create(
                            name=products_list['products'][i]['product_name_fr'],
                            score=products_list['products'][i]['nutrition_grades'],
                            score_image=score_image_url)
                        # add needed info to product
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
                        # browse categories_tags to add categories to product
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

    # get categories list from API
    categories_list = access_url(CATEGORIES_LIST_URL)
    # browse categories
    for i, category in enumerate(categories_list['tags']):
        # create Category instance if category doesn't already exist and has a name and an id
        if categories_list['tags'][i]['name'] and categories_list['tags'][i]['id'] and not \
                Category.objects.filter(name=categories_list['tags'][i]['name']).exists():
            category = Category.objects.create(name=categories_list['tags'][i]['name'],
                                               tag=categories_list['tags'][i]['id'])
            category.save()

    print("Toutes les catégories ont été ajoutées à la base de données !")


def get_products_search(request):
    """searches product matching the user's request"""

    # create global variables to prevent losing variables during pagination
    global PRODUCTS_LIST
    global QUERY

    # if this is a POST request we need to process the request
    if request.method == "POST":
        # retrieve search parameter
        query = request.POST.get('search')

        # if query exists
        if query:
            # get products that match query
            PRODUCTS_LIST = Product.objects.filter(name__icontains=query).order_by('name')
            QUERY = query

    return display_products(request, PRODUCTS_LIST, QUERY)


def get_substitutes(request, product_id):
    """finds substitutes matching the user's chosen product"""

    # get product to substitute
    product = Product.objects.get(pk=product_id)
    # get categories from product to substitute
    categories = product.categories.values_list('id', flat=True)
    # turn the query set into a list to use later
    categories_list = list(categories)

    # get temporary substitutes with matching categories to original product as a list to use later
    temporary_substitutes = list(Product.objects.filter(score__lte=product.score).filter(
        categories__in=categories).order_by('score').exclude(id=product_id))

    # create dictionary to save potential substitutes' id as key
    # and the number of matching categories with original product as value
    categories_occurrence_dict = dict()

    # browse temporary substitutes
    for product in temporary_substitutes:
        # set value for substitute id to 0
        categories_occurrence_dict[product.id] = 0
        # get a list of categories for every potential substitute
        substitutes_categories_list = list(product.categories.values_list('id', flat=True))
        # browse original product's categories
        for i in categories_list:
            # browse each potential substitute's categories
            for cat in substitutes_categories_list:
                # if category form original product and potential substitute match
                if cat == i:
                    # add an occurrence to dict
                    categories_occurrence_dict[product.id] += 1

    # sort categories occurrence dict to get the potential substitutes
    # with the most matching categories and limit result to 12 substitutes
    sorted_substitutes = sorted(categories_occurrence_dict.items(), key=lambda x: x[1],
                                reverse=True)[:12]

    # turn sorted substitutes into a list of the substitutes ids
    substitutes_id_list = list(map(lambda x: x[0], sorted_substitutes))

    #  get final query set with the products who match the identified substitutes id
    substitutes_list = Product.objects.filter(id__in=substitutes_id_list)

    return display_products(request, substitutes_list, query=None)


def get_saved_substitutes(request):
    """finds the user's saved products"""

    # get current user
    user = User.objects.get(pk=request.user.id)
    # get substitutes id for current user
    substitutes_id_list = Substitute.objects.filter(user=user).values_list('id')
    # get products that match the substitutes id
    substitutes_list = Product.objects.filter(id__in=substitutes_id_list).order_by('id')

    return display_products(request, substitutes_list, query=None)


def display_products(request, products_list, query):
    """returns context to be displayed by template with paginated products list"""

    # set paginator with products_list and number of products per page
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

    # set context with paginated products
    context = {
        'products': products,
        'search': query,
        'paginate': True,
    }

    return context
