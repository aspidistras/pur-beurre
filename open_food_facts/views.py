"""views creating module"""

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from sentry_sdk import capture_message

from .models import Product, Substitute
from .forms import LoginForm, UserForm
# import methods to use in views
from .utils import get_substitutes, get_saved_substitutes, get_products_search


def index(request):
    """displays the main page"""

    template = loader.get_template("open_food_facts/index.html")
    return HttpResponse(template.render(request=request))


def page_not_found(request, exception):
    capture_message("Page not found", level="error")

    # return any response here, e.g.:
    return render(request, "404.html")


def internal_server_error(request, exception):
    capture_message("Internal server error", level="error")

    # return any response here, e.g.:
    return render(request, "500.html")


def legal_notices(request):
    """displays the legal notices page with credits and resources"""

    template = loader.get_template("open_food_facts/legal-notices.html")
    return HttpResponse(template.render(request=request))


def get_user(request):
    """displays the sign in page in order for the user to create an account"""

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data and create new user with processed data
            user = User.objects.create_user(username=form.cleaned_data['username'],
                                            first_name=form.cleaned_data['first_name'],
                                            last_name=form.cleaned_data['last_name'],
                                            email=form.cleaned_data['email'],
                                            password=form.cleaned_data['password'])
            user.save()
            form.clean()

            capture_message("New user has created an account")
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UserForm()

    return render(request, 'open_food_facts/create-account.html', {'form': form})


def thanks(request):
    """displays a thanking message for creating an account"""

    template = loader.get_template("open_food_facts/thanks.html")
    return HttpResponse(template.render(request=request))


def user_login(request):
    """displays the log in page in order for the user to access his account"""

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data and authenticate user with processed data
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                # A backend authenticated the credentials
                if user.is_active:
                    login(request, user)
                    # redirects to user's account
                    return HttpResponseRedirect('/account/')

                # No backend authenticated the credentials
                return HttpResponseRedirect('/login-error/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LoginForm()

    return render(request, 'open_food_facts/login.html', {'form': form})


@login_required
def account(request):
    """displays the user's account page with his data"""

    template = loader.get_template("open_food_facts/account.html")
    return HttpResponse(template.render(request=request))


def details(request, product_id):
    """displays the matching product's details"""

    # get product, if it doesn't exist display 404 error template
    product = get_object_or_404(Product, pk=product_id)
    if request.user.is_authenticated:
        user_saved_substitutes = Substitute.objects.filter(user=request.user, product=product)
        if len(user_saved_substitutes) != 0:
            add = False
        else:
            add = True
    else:
        add = True

    return render(request, "open_food_facts/product.html", {'product': product, 'add': add})


@login_required
def user_logout(request):
    """logs out the user and redirects to index page"""

    logout(request)
    # redirect to index when user is logged out
    return HttpResponseRedirect('/')


def search_products(request):
    """calls the search products method
    that returns a list of products matching to the search argument"""

    # call get_products_search function
    products = get_products_search(request)
    # if no products were found
    if len(products['products']) == 0:
        # no need for pagination
        products['paginate'] = False
        capture_message("No results for this search", level="warning")
        # displays a page to tell the user that there were no results to his search
        # and invite him to search another keyword
        return render(request, "open_food_facts/search-no-result.html", products)

    # displays a page (or multiple) with the list of products found
    return render(request, "open_food_facts/results-products.html", products)


def search_substitutes(request, product_id):
    """calls the get substitutes method in order to find products
    that could substitute the one chosen by the user"""

    # call get_substitutes function
    substitutes = get_substitutes(request, product_id)
    substitutes['product_to_substitute'] = Product.objects.filter(id=product_id)
    # if no products were found
    if len(substitutes['products']) == 0:
        # no need for pagination
        substitutes['paginate'] = False
        capture_message("No substitute for this product", level="warning")
        # displays a page to tell the user that there were no results to his search
        # and invite him to search another keyword
        return render(request, "open_food_facts/search-no-result.html", substitutes)
    # displays a page (or multiple) with the list of potential substitutes found
    return render(request, "open_food_facts/results-substitutes.html", substitutes)


@login_required
def save_substitute(request, product_id):
    """creates a Substitute instance with the related user and product"""

    # get current user
    user = User.objects.get(pk=request.user.id)
    # get product to save
    product = Product.objects.get(pk=product_id)
    # create substitute with related user and product
    substitute = Substitute.objects.create(user=user, product=product)
    substitute.save()
    # create a message to confirm the substitute was saved, to be displayed on the product page
    messages.success(request, 'Le produit " ' + product.name
                     + ' " a bien été enregistré dans vos produits !')
    add = False
    # stay on the product's page with success message loaded
    return render(request, "open_food_facts/product.html", {'product': product, 'add': add})


@login_required
def user_products(request):
    """gets all of a user's saved products and displays them"""

    # call get_saved_substitute function
    products = get_saved_substitutes(request)
    # if no products were found
    if len(products['products']) == 0:
        # no need for pagination
        products['paginate'] = False
        # displays a page to tell the user that he hasn't saved any products yet
        # and invite him to start searching for products
        return render(request, "open_food_facts/user-no-result.html", products)

    # displays a page (or multiple) with the list of products found
    return render(request, "open_food_facts/user-substitutes.html", products)


@login_required
def unsave_product(request, product_id):
    """deletes a substitute instance to remove a product from user's favorites"""

    user = User.objects.get(id=request.user.id)
    product = Product.objects.get(id=product_id)
    substitute = Substitute.objects.get(user_id=user.id, product_id=product.id)
    substitute.delete()
    add = True

    return render(request, "open_food_facts/product.html", {'product': product, 'add': add})
