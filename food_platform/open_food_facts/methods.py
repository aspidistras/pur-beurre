import requests
import json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .constants import CATEGORIES_LIST_URL, PRODUCTS_LIST_URL, SCORES_LIST
from .models import Category, Product, Substitute


def access_url(url):
    request = requests.get(url)
    result = json.loads(request.text)
    return result


def get_categories():
    categories_list = access_url(CATEGORIES_LIST_URL)
    for i, c in enumerate(categories_list['tags']):
        if categories_list['tags'][i]['name'] and categories_list['tags'][i]['id'] and not \
                Category.objects.filter(name=categories_list['tags'][i]['name']).exists():
            category = Category.objects.create(name=categories_list['tags'][i]['name'],
                                               tag=categories_list['tags'][i]['id'])
            category.save()


def get_products():
    for score in SCORES_LIST:
        products_list = access_url(PRODUCTS_LIST_URL.format(score))
        for i, p in enumerate(products_list['products']):
            if products_list['products'][i]['product_name_fr'] and products_list['products'][i]['nutrition_grades'] and not Product.objects.filter(name=products_list['products'][i]['product_name_fr']).exists():
                product = Product.objects.create(name=products_list['products'][i]['product_name_fr'],
                                                 score=products_list['products'][i]['nutrition_grades'])
                product.save()
                for category in products_list['products'][i]['categories_tags']:
                    category = Category.objects.filter(tag=category).values('id')
                    product.category.add(category[0]['id'])
                    product.save()


def get_substitute(request):
    substitutes_list = Product.objects.filter(score=request.GET['search'])[:24]
    return display_products(request, substitutes_list)


def save_substitute(request):
    substitute = Substitute.create(name=request.GET['name'], score=request.GET['score'],
                                   category=request.GET['category'], user_id=request.GET['user_id'])
    substitute.save()


def get_saved_substitutes(request):
    substitutes_list = Substitute.objects.filter(user_id=request.GET['user_id'])
    return display_products(request, substitutes_list)


def display_products(request, products_list):
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
        'paginate': True
    }
    return context

