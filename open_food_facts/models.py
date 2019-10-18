"""models creating module"""

from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """model defining categories attributes"""

    name = models.CharField(max_length=150, unique=True)
    tag = models.CharField(max_length=150, unique=True)


class Product(models.Model):
    """model defining products attributes"""

    name = models.CharField(max_length=200, unique=True)
    score = models.CharField(max_length=1)
    score_image = models.ImageField(max_length=300)
    image = models.ImageField(max_length=300, null=True)
    calories = models.FloatField(null=True)
    fats = models.FloatField(null=True)
    carbs = models.FloatField(null=True)
    proteins = models.FloatField(null=True)
    salt = models.FloatField(null=True)
    url = models.URLField(max_length=300, null=True)
    categories = models.ManyToManyField(Category)


class Substitute(models.Model):
    """model defining substitutes attributes"""

    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
