from django.shortcuts import render

# Create your views here.


from django.http import HttpResponse


def index(request):
    message = "Salut tout le monde !"
    return HttpResponse(message)
