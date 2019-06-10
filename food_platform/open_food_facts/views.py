from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import UserForm
from .forms import LoginForm


def index(request):
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


def product(request):
    template = loader.get_template("open_food_facts/product.html")
    return HttpResponse(template.render(request=request))


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')




