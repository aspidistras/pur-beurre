import requests
import json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import IntegrityError
from .constants import CATEGORIES_LIST_URL, PRODUCTS_LIST_URL, SCORES_LIST, SCORE_IMAGES_LIST
from .models import Category, Product, User


def access_url(url):
    request = requests.get(url)
    result = json.loads(request.text)
    return result


def get_products():
    for score in SCORES_LIST:
        products_list = access_url(PRODUCTS_LIST_URL.format(score))
        for i, p in enumerate(products_list['products']):
            try:
                if products_list['products'][i]['product_name_fr'] and not \
                        Product.objects.filter(name=products_list['products'][i]['product_name_fr']).exists():
                    product = Product.objects.create(
                        name=products_list['products'][i]['product_name_fr'],
                        score=products_list['products'][i]['nutrition_grades'],
                        image=products_list['products'][i]['image_small_url'],
                        calories=products_list['products'][i]['nutriments']['energy_100g'],
                        fats=products_list['products'][i]['nutriments']['fat_100g'],
                        carbs=products_list['products'][i]['nutriments']['carbohydrates_100g'],
                        proteins=products_list['products'][i]['nutriments']['proteins_100g'],
                        salt=products_list['products'][i]['nutriments']['sodium_100g'],
                        url=products_list['products'][i]['url'])
                    product.save()
                    for cat in products_list['products'][i]['categories_tags']:
                        category = Category.objects.filter(tag=cat)
                        product.categories.add(*category)
                        product.save()
            except KeyError or IntegrityError:
                pass


def get_categories():
    categories_list = access_url(CATEGORIES_LIST_URL)
    for i, c in enumerate(categories_list['tags']):
        if categories_list['tags'][i]['name'] and categories_list['tags'][i]['id'] and not \
                Category.objects.filter(name=categories_list['tags'][i]['name']).exists():
            category = Category.objects.create(name=categories_list['tags'][i]['name'],
                                               tag=categories_list['tags'][i]['id'])
            category.save()


def get_substitutes(request):
    substitutes_list = Product.objects.filter(score=request.POST.get('search'))[:24]
    substitutes_list = Product.objects.all()
    return display_products(request, substitutes_list)


def save_substitute(request):
    user = User.objects.get(pk=request.POST['user_id'])
    substitute = user.substitutes.add(Product.objects.get(pk=request.POST['product_id']))
    substitute.save()


def get_saved_substitutes(request):
    user_id = request.user.id
    user = User.objects.get(pk=user_id)
    substitutes_list = user.substitutes
    return display_products(request, substitutes_list)


def display_products(request, products_list):
    paginator = Paginator(products_list, 6)
    page = request.GET.get('page')
    try:
        products = paginator.get_page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)

    print(len(products_list))

    if len(products_list) <= 6 and len(products_list) > 0:
        context = {
            'products': products,
            'paginate': False,
            'empty': False
        }
    elif len(products_list) > 6:
        context = {
            'products': products,
            'paginate': True,
            'empty': False
        }
    else:
        context = {
            'products': products,
            'paginate': False,
            'empty': True
        }

    context = {'products': products}
    return context

