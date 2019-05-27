from django.db import models
from django.forms import ModelForm

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    score = models.IntegerField()
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)


class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(max_length=200, unique=True)
    password = models.CharField(max_length=50)


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'name', 'surname', 'email', 'password']
        labels = {
            'username': 'Pseudo', 'name': 'Prénom', 'surname': 'Nom', 'password': 'Mot de passe',
        }


