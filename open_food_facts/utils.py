"""methods to access and manage data module"""

import json
import requests

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .constants import SCORE_IMAGES_LIST, SEARCH_URL

# uncomment to get all products
# from .constants import PRODUCTS_INFO_URL, CATEGORIES_LIST_URL, PRODUCTS_LIST_URL,
# SCORES_LIST, MAX_PAGES_NUMBER

from .models import Category, Product, Substitute, User


def access_url(url, parameters):
    """returns json result when accessing an url"""

    request = requests.get(url, params=parameters)
    # get json result for url
    result = json.loads(request.text)
    return result


def create_products(products):
    """browses a list of products to create Product instances"""

    for product in products:
        # create Product instance if product doesn't already exist and has a french name
        try:
            if not Product.objects.filter(url=product['url']).exists():
                prod = Product.objects.create(
                    name=product['product_name'],
                    score=product['nutrition_grade_fr'],
                    score_image=SCORE_IMAGES_LIST[product['nutrition_grade_fr']],
                    image=product['image_small_url'],
                    calories=product['nutriments']['energy_value'],
                    fats=product['nutriments']['fat_100g'],
                    carbs=product['nutriments']['carbohydrates_100g'],
                    proteins=product['nutriments']['proteins_100g'],
                    salt=product['nutriments']['sodium_100g'],
                    url=product['url'])
                # browse categories_tags to add categories to product
                for cat in product['categories_tags']:
                    if not Category.objects.filter(tag=cat).exists():
                        category = Category.objects.create(tag=cat)
                        prod.categories.add(category)

                    else:
                        category = Category.objects.filter(tag=cat)
                        prod.categories.add(*category)

                    prod.save()
        except KeyError:
            continue


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
            parameters = {
                'action': 'process',
                'page_size': '30',
                'search_terms': query,
                'json': '1',
            }

            potential_products_list = Product.objects.filter(name__icontains=query)
            if len(potential_products_list) < 6:
                products = access_url(SEARCH_URL, parameters)
                create_products(products['products'])

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
    potential_substitutes = list(Product.objects.filter(score__lt=product.score).filter(
        categories__in=categories).order_by('score').exclude(id=product_id))

    if len(potential_substitutes) < 6:
        # get categories from product to substitute
        categories_tag = product.categories.values_list('tag', flat=True)
        # turn the query set into a list to use later
        categories_list_tag = list(categories_tag)
        for cat in categories_list_tag:
            parameters = {
                'action': 'process',
                'tagtype_0': 'categories',
                'tag_contains_0': 'contains',
                'tag_0': cat,
                'page_size': '30',
                'json': '1',
            }

            products = access_url(SEARCH_URL, parameters)
            create_products(products['products'])

    temporary_substitutes = list(Product.objects.filter(score__lt=product.score).
                                 filter(categories__in=categories).order_by('score').
                                 exclude(id=product_id))

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
                                reverse=True)[:6]

    # turn sorted substitutes into a list of the substitutes ids
    substitutes_id_list = list(map(lambda x: x[0], sorted_substitutes))

    #  get final query set with the products who match the identified substitutes id
    substitutes_list = Product.objects.filter(id__in=substitutes_id_list).order_by('score')

    return display_products(request, substitutes_list, query=None)


def get_saved_substitutes(request):
    """finds the user's saved products"""

    # get current user
    user = User.objects.get(pk=request.user.id)
    # get substitutes id for current user
    substitutes_id_list = Substitute.objects.filter(user=user).values_list('product')
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


# uncomment and call functions to directly fill local database with categories and products

'''
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
            create_products(products_list)

    print("Tous les produits ont été ajoutés à la base de données !")'''
