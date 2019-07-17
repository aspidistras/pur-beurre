from django.shortcuts import render

# Create your views here.

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import UserForm, Product, Category
from .forms import LoginForm
from .methods import get_products, get_categories, display_products, get_substitutes, get_saved_substitutes


def index(request):
    """get_categories()"""
    get_products()
    template = loader.get_template("open_food_facts/index.html")
    return HttpResponse(template.render(request=request))


def get_user(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            # process the data in form.cleaned_data as required
            user = User.objects.create_user(username=form.cleaned_data['username'],
                                            first_name=form.cleaned_data['name'],
                                            last_name=form.cleaned_data['surname'],
                                            email=form.cleaned_data['email'],
                                            password=form.cleaned_data['password'])
            user.save()
            form.clean()

            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UserForm()

    return render(request, 'open_food_facts/create-account.html', {'form': form})


def thanks(request):
    template = loader.get_template("open_food_facts/thanks.html")
    return HttpResponse(template.render(request=request))


def user_login(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                # A backend authenticated the credentials
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/account/')
            else:
                # No backend authenticated the credentials
                return HttpResponseRedirect('/login-error/')
    else:
        form = LoginForm()

    return render(request, 'open_food_facts/login.html', {'form': form})


def account(request):
    template = loader.get_template("open_food_facts/account.html")
    return HttpResponse(template.render(request=request))


def details(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, "open_food_facts/product.html", {'product': product})


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def search(request):
    substitutes = get_substitutes(request)
    """if substitutes['empty'] is True:
        return render(request, "open_food_facts/search-no-result.html", substitutes)
    else:"""
    return render(request, "open_food_facts/results-products.html", substitutes)


def user_products(request):
    substitutes = get_saved_substitutes(request)
    if substitutes['empty'] is True:
        return render(request, "open_food_facts/user-no-result.html", substitutes)
    else:
        return render(request, "open_food_facts/listing.html", substitutes)



