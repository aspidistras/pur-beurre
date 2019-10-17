import requests
import json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import DataError
from django.core.exceptions import ValidationError

from .constants import CATEGORIES_LIST_URL, PRODUCTS_LIST_URL, SCORES_LIST, SCORE_IMAGES_LIST, \
    PRODUCTS_INFO_URL
from .models import Category, Product, Substitute, User


def access_url(url):
    request = requests.get(url)
    result = json.loads(request.text)
    return result


def get_products():
    for score in SCORES_LIST:
        products_list_info = access_url(PRODUCTS_INFO_URL.format(score))
        pages_count = int(products_list_info['count'] / 20 + 1)
        for page in range(pages_count):
            products_list = access_url(PRODUCTS_LIST_URL.format(score, page))
            for i, p in enumerate(products_list['products']):
                for score_image_url in SCORE_IMAGES_LIST:
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
                        pass


def get_categories():
    categories_list = access_url(CATEGORIES_LIST_URL)
    for i, c in enumerate(categories_list['tags']):
        if categories_list['tags'][i]['name'] and categories_list['tags'][i]['id'] and not \
                Category.objects.filter(name=categories_list['tags'][i]['name']).exists():
            category = Category.objects.create(name=categories_list['tags'][i]['name'],
                                               tag=categories_list['tags'][i]['id'])
            category.save()


def get_products_search(request):

    global PRODUCTS_LIST
    global QUERY

    if request.method == "POST":
        query = request.POST.get('search')

        if query:
            PRODUCTS_LIST = Product.objects.filter(name__icontains=query).order_by('name')
            QUERY = query

    return display_products(request, PRODUCTS_LIST, QUERY)


def get_substitutes(request, product_id):
    product = Product.objects.get(pk=product_id)
    categories = product.categories.values_list('id')
    substitutes_list = Product.objects.filter(score__lte=product.score).filter(
        categories__in=categories).order_by('name')[:24]

    return display_products(request, substitutes_list, query=None)


def get_saved_substitutes(request):
    user = User.objects.get(pk=request.user.id)
    substitutes_id_list = Substitute.objects.filter(user=user).values_list('id')
    substitutes_list = Product.objects.filter(id__in=substitutes_id_list).order_by('id')
    return display_products(request, substitutes_list, query=None)


def display_products(request, products_list, query):
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
