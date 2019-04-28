from django.db import models

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    score = models.IntegerField()
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)


