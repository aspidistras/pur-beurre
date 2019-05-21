from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from .models import UserForm, User


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

            user = User()
            # process the data in form.cleaned_data as required
            user.username = form.cleaned_data['username']
            user.name = form.cleaned_data['name']
            user.surname = form.cleaned_data['surname']
            user.email = form.cleaned_data['email']
            user.password = form.cleaned_data['password']
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
